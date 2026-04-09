# -*- coding: utf-8 -*-
from datetime import date
from unittest.mock import patch

import requests
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from core.services.ai_recommendations import (
    _cache_key,
    _cache_set_safe,
    _extract_output_text,
    _request_openai,
    _seo_prompt_payload,
    get_conversion_ai_recommendations,
    get_seo_ai_recommendations,
)


def _mock_response(*, status_code: int, payload: dict):
    class _Response:
        def __init__(self, code: int, body: dict):
            self.status_code = code
            self._body = body
            self.headers = {}

        def json(self):
            return self._body

    return _Response(status_code, payload)


def _seo_audit_payload(**overrides):
    payload = {
        "domain": "example.com",
        "score": 61,
        "seo_score": 61,
        "pages_count": 5,
        "has_robots_txt": True,
        "has_sitemap_xml": True,
        "pages_with_speed_issues": 1,
        "pages_with_indexing_issues": 1,
        "avg_ttfb_ms": 430,
        "avg_performance_score": 72,
        "errors": [],
        "issue_groups": [],
        "breakdown": {"high_issues": 1, "medium_issues": 1, "low_issues": 0},
    }
    payload.update(overrides)
    return payload


@override_settings(
    OPENAI_API_KEY="test-key",
    AI_RECOMMENDATIONS_ENABLED=True,
    AI_RECOMMENDATIONS_TIMEOUT_SECONDS=10,
    AI_RECOMMENDATIONS_TTL_SECONDS=300,
    AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS=900,
    AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_SEO=700,
    AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_CONVERSION=900,
    AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_RETRY_CAP=1200,
    OPENAI_MODEL_SEO="gpt-5-mini",
    OPENAI_MODEL_CONVERSION="gpt-5-mini",
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ai-recommendations-tests",
        }
    },
)
class AIRecommendationsServiceTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    @patch("core.services.ai_recommendations.requests.post")
    def test_request_openai_omits_temperature_for_gpt5_models(self, mocked_post):
        mocked_post.return_value = _mock_response(status_code=200, payload={"output_text": '{"recommendations":[]}'})

        _request_openai(model="gpt-5-mini", system_prompt="system", user_prompt="user")

        body = mocked_post.call_args.kwargs["json"]
        self.assertEqual(body.get("model"), "gpt-5-mini")
        self.assertEqual(body.get("instructions"), "system")
        self.assertEqual(body.get("input"), "user")
        self.assertGreater(int(body.get("max_output_tokens") or 0), 0)
        self.assertNotIn("reasoning", body)
        self.assertNotIn("text", body)
        self.assertNotIn("temperature", body)

    @patch("core.services.ai_recommendations.requests.post")
    def test_request_openai_minimal_payload_for_non_gpt5_models(self, mocked_post):
        mocked_post.return_value = _mock_response(status_code=200, payload={"output_text": '{"recommendations":[]}'})

        _request_openai(model="gpt-4.1-mini", system_prompt="system", user_prompt="user")

        body = mocked_post.call_args.kwargs["json"]
        self.assertEqual(body.get("model"), "gpt-4.1-mini")
        self.assertEqual(body.get("instructions"), "system")
        self.assertEqual(body.get("input"), "user")
        self.assertNotIn("temperature", body)
        self.assertNotIn("reasoning", body)
        self.assertNotIn("text", body)

    def test_extract_output_text_from_top_level_output_text(self):
        text = _extract_output_text({"output_text": '  {"recommendations":[]}  '})
        self.assertEqual(text, '{"recommendations":[]}')

    def test_extract_output_text_from_output_content_text(self):
        payload = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "text",
                            "text": {"value": '{"recommendations":[{"problem":"P","severity":"high","fix":"F"}]}'},
                        }
                    ],
                }
            ]
        }
        text = _extract_output_text(payload)
        self.assertIn('"recommendations"', text)

    def test_extract_output_text_from_nested_unexpected_fields(self):
        payload = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "json",
                            "payload": {
                                "result": {
                                    "final_answer": '{"recommendations":[{"problem":"nested","severity":"medium","fix":"ok"}]}'
                                }
                            },
                        }
                    ],
                }
            ]
        }
        text = _extract_output_text(payload)
        self.assertIn('"problem":"nested"', text)

    def test_seo_prompt_payload_is_compact(self):
        payload = _seo_prompt_payload(
            {
                "domain": "example.com",
                "seo_score": 58,
                "pages_count": 12,
                "issue_groups": [
                    {
                        "issue_type": "missing_title",
                        "title": "Missing title",
                        "severity": "high",
                        "pages_affected": 7,
                        "pages": ["https://example.com/a", "https://example.com/b", "https://example.com/c"],
                    }
                ],
            }
        )
        self.assertEqual(set(payload.keys()), {"domain", "seo_score", "pages_count", "problems"})
        self.assertTrue(isinstance(payload.get("problems"), list))
        self.assertEqual(payload["problems"][0]["problem"], "Missing title")
        self.assertLessEqual(len(payload["problems"][0]["pages"]), 2)
        self.assertNotIn("overview", payload)
        self.assertNotIn("fix_plan", payload)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_recommendations_ignores_cached_fallback_payload(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "output_text": (
                    '{"recommendations":[{"problem":"Missing title","severity":"high","fix":"Add title 50-60 chars."}]}'
                )
            },
        )

        audit_payload = _seo_audit_payload(
            issue_groups=[
                {
                    "issue_type": "missing_title",
                    "title": "Missing title",
                    "severity": "high",
                    "pages_affected": 3,
                    "pages": ["https://example.com/"],
                }
            ]
        )
        prepared = _seo_prompt_payload(audit_payload)
        cache_key = _cache_key(
            module="seo",
            model="gpt-5-mini",
            scope="client:1:audit:10",
            payload=prepared,
        )
        _cache_set_safe(
            cache_key,
            {
                "success": True,
                "source": "fallback",
                "fallback": True,
                "recommendations": [],
            },
            ttl_seconds=300,
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=10,
            audit_payload=audit_payload,
            force_refresh=False,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "openai")
        self.assertFalse(result["fallback"])
        self.assertGreaterEqual(len(result.get("recommendations") or []), 1)
        mocked_post.assert_called_once()

    @patch("core.services.ai_recommendations.requests.post")
    def test_conversion_recommendations_parse_plain_text_response(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={"output_text": "1. Simplify form.\n2. Improve CTA contrast."},
        )

        summary_payload = {
            "visitors_unique": 12,
            "ai_event_signals": {
                "overview": {
                    "unique_users_total": 12,
                    "avg_scroll_depth": 44.5,
                    "form_started_users": 4,
                    "form_submit_success_users": 1,
                    "cta_click_users": 3,
                    "micro_conversion_users": 2,
                },
                "form_funnel": {"rows": [{"stage": "form_visible", "users": 12, "next_step_rate_pct": 33.3}]},
                "cta_funnel": {"rows": [{"cta_id": "hero", "cta_text": "Send request", "clicks": 3}]},
                "field_analytics": {"rows": []},
                "section_analytics": {"rows": []},
                "source_segmentation": {"rows": []},
                "device_segmentation": {"rows": []},
                "micro_conversions": {"rows": []},
                "anomalies": {"rows": []},
            },
        }

        result = get_conversion_ai_recommendations(
            client_id=1,
            period_from=date(2026, 3, 1),
            period_to=date(2026, 3, 16),
            summary_payload=summary_payload,
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "ai")
        self.assertGreaterEqual(len(result.get("items") or []), 1)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_recommendations_parse_output_content_when_output_text_is_missing(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "status": "completed",
                "output": [
                    {"type": "reasoning", "summary": []},
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": (
                                    '{"recommendations":[{"problem":"Missing description","severity":"medium",'
                                    '"fix":"Add unique description 120-160 chars."}]}'
                                ),
                            }
                        ],
                    },
                ],
            },
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=11,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "openai")
        self.assertFalse(result["fallback"])
        self.assertEqual(set(result.keys()), {"success", "source", "fallback", "recommendations"})
        self.assertGreaterEqual(len(result.get("recommendations") or []), 1)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_incomplete_with_partial_text_uses_ai_without_retry(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "status": "incomplete",
                "incomplete_details": {"reason": "max_output_tokens"},
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": (
                                    '{"recommendations":[{"problem":"Slow TTFB","severity":"high",'
                                    '"fix":"Enable caching and tune backend response time."}]}'
                                ),
                            }
                        ],
                    }
                ],
            },
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=111,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "openai")
        self.assertEqual(mocked_post.call_count, 1)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_incomplete_without_text_retries_and_succeeds(self, mocked_post):
        mocked_post.side_effect = [
            _mock_response(
                status_code=200,
                payload={
                    "status": "incomplete",
                    "incomplete_details": {"reason": "max_output_tokens"},
                    "output": [{"type": "reasoning", "summary": []}],
                },
            ),
            _mock_response(
                status_code=200,
                payload={
                    "status": "completed",
                    "output_text": (
                        '{"recommendations":[{"problem":"Missing canonical","severity":"medium",'
                        '"fix":"Set canonical URL for duplicate pages."}]}'
                    ),
                },
            ),
        ]

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=112,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "openai")
        self.assertEqual(mocked_post.call_count, 2)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_retry_uses_module_token_limits(self, mocked_post):
        mocked_post.side_effect = [
            _mock_response(status_code=200, payload={"status": "completed", "output": []}),
            _mock_response(
                status_code=200,
                payload={
                    "status": "completed",
                    "output_text": (
                        '{"recommendations":[{"problem":"Missing H1","severity":"medium","fix":"Add one H1 per page."}]}'
                    ),
                },
            ),
        ]

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=113,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "openai")
        self.assertEqual(mocked_post.call_count, 2)

        first_max_tokens = mocked_post.call_args_list[0].kwargs["json"]["max_output_tokens"]
        second_max_tokens = mocked_post.call_args_list[1].kwargs["json"]["max_output_tokens"]
        self.assertEqual(first_max_tokens, 700)
        self.assertGreater(second_max_tokens, first_max_tokens)
        self.assertLessEqual(second_max_tokens, 1200)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_retry_without_usable_text_returns_fallback(self, mocked_post):
        mocked_post.side_effect = [
            _mock_response(
                status_code=200,
                payload={
                    "status": "incomplete",
                    "incomplete_details": {"reason": "max_output_tokens"},
                    "output": [],
                },
            ),
            _mock_response(
                status_code=200,
                payload={
                    "status": "incomplete",
                    "incomplete_details": {"reason": "max_output_tokens"},
                    "output": [],
                },
            ),
        ]

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=114,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "fallback")
        self.assertTrue(result.get("fallback"))
        self.assertTrue(isinstance(result.get("recommendations"), list))
        self.assertEqual(mocked_post.call_count, 2)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_parse_json_string_wrapped_output_text(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "status": "completed",
                "output_text": (
                    '"{\\"recommendations\\":[{\\"problem\\":\\"Wrapped\\",\\"severity\\":\\"low\\",'
                    '\\"fix\\":\\"Use shorter title\\"}]}"'
                ),
            },
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=115,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "openai")
        self.assertEqual(result["recommendations"][0]["problem"], "Wrapped")

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_nonstandard_output_item_structure_is_extracted(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "json",
                                "payload": {
                                    "result": {
                                        "answer": (
                                            '{"recommendations":[{"problem":"Nested path","severity":"medium",'
                                            '"fix":"Fix nested response parsing."}]}'
                                        )
                                    }
                                },
                            }
                        ],
                    }
                ],
            },
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=117,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "openai")
        self.assertEqual(result["recommendations"][0]["problem"], "Nested path")

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_completed_empty_output_fallback_after_retry(self, mocked_post):
        mocked_post.side_effect = [
            _mock_response(status_code=200, payload={"status": "completed", "output": []}),
            _mock_response(status_code=200, payload={"status": "completed", "output": []}),
        ]

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=116,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "fallback")
        self.assertTrue(result.get("fallback"))
        self.assertEqual(mocked_post.call_count, 2)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_response_with_three_recommendations(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "status": "completed",
                "output_text": (
                    '{"recommendations":['
                    '{"problem":"P1","severity":"high","fix":"F1"},'
                    '{"problem":"P2","severity":"medium","fix":"F2"},'
                    '{"problem":"P3","severity":"low","fix":"F3"}]}'
                ),
            },
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=118,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(len(result.get("recommendations") or []), 3)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_response_with_ten_recommendations_and_severity_sort(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "status": "completed",
                "output_text": (
                    '{"recommendations":['
                    '{"problem":"L1","severity":"low","fix":"f"},'
                    '{"problem":"H1","severity":"high","fix":"f"},'
                    '{"problem":"M1","severity":"medium","fix":"f"},'
                    '{"problem":"L2","severity":"low","fix":"f"},'
                    '{"problem":"H2","severity":"high","fix":"f"},'
                    '{"problem":"M2","severity":"medium","fix":"f"},'
                    '{"problem":"L3","severity":"low","fix":"f"},'
                    '{"problem":"H3","severity":"high","fix":"f"},'
                    '{"problem":"M3","severity":"medium","fix":"f"},'
                    '{"problem":"H4","severity":"high","fix":"f"},'
                    '{"problem":"M4","severity":"medium","fix":"f"},'
                    '{"problem":"L4","severity":"low","fix":"f"}]}'
                ),
            },
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=119,
            audit_payload=_seo_audit_payload(),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        recommendations = result.get("recommendations") or []
        self.assertEqual(len(recommendations), 10)
        weights = {"high": 0, "medium": 1, "low": 2}
        severity_order = [weights.get(item.get("severity"), 3) for item in recommendations]
        self.assertEqual(severity_order, sorted(severity_order))

    @patch(
        "core.services.ai_recommendations.requests.post",
        side_effect=requests.exceptions.ReadTimeout("openai timeout"),
    )
    def test_seo_recommendations_timeout_returns_compact_fallback(self, mocked_post):
        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=14,
            audit_payload=_seo_audit_payload(
                issue_groups=[
                    {
                        "issue_type": "missing_title",
                        "title": "Missing title",
                        "severity": "high",
                        "pages_affected": 2,
                        "pages": ["https://example.com/"],
                    }
                ]
            ),
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "fallback")
        self.assertTrue(result.get("fallback"))
        self.assertTrue(isinstance(result.get("recommendations"), list))
        self.assertEqual(mocked_post.call_count, 1)

    @patch(
        "core.services.ai_recommendations.requests.post",
        side_effect=requests.exceptions.ConnectionError("openai unavailable"),
    )
    def test_conversion_recommendations_network_error_stays_openai_error(self, mocked_post):
        result = get_conversion_ai_recommendations(
            client_id=1,
            period_from=date(2026, 3, 1),
            period_to=date(2026, 3, 16),
            summary_payload={"visitors_unique": 0, "ai_event_signals": {}},
            force_refresh=True,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["source"], "openai_error")
        self.assertIn("debug", result)
        self.assertEqual(mocked_post.call_count, 1)
