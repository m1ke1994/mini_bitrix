# -*- coding: utf-8 -*-
from datetime import date
from unittest.mock import patch

import requests
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from core.services.ai_recommendations import (
    _cache_key,
    _cache_set_safe,
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

        def json(self):
            return self._body

    return _Response(status_code, payload)


@override_settings(
    OPENAI_API_KEY="test-key",
    AI_RECOMMENDATIONS_ENABLED=True,
    AI_RECOMMENDATIONS_TIMEOUT_SECONDS=10,
    AI_RECOMMENDATIONS_TTL_SECONDS=300,
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
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={"output_text": '{"title":"x","summary":"y","items":["z"],"priority":"high"}'},
        )

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
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={"output_text": '{"title":"x","summary":"y","items":["z"],"priority":"high"}'},
        )

        _request_openai(model="gpt-4.1-mini", system_prompt="system", user_prompt="user")

        body = mocked_post.call_args.kwargs["json"]
        self.assertEqual(body.get("model"), "gpt-4.1-mini")
        self.assertEqual(body.get("instructions"), "system")
        self.assertEqual(body.get("input"), "user")
        self.assertNotIn("temperature", body)
        self.assertNotIn("reasoning", body)
        self.assertNotIn("text", body)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_recommendations_ignores_cached_fallback_payload(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "output_text": (
                    '{"title":"AI-рекомендации по SEO","summary":"Есть точки роста.","items":["Исправьте title"],'
                    '"priority":"high"}'
                )
            },
        )

        audit_payload = {
            "domain": "example.com",
            "score": 61,
            "seo_score": 61,
            "pages_count": 3,
            "has_robots_txt": True,
            "pages_with_speed_issues": 1,
            "pages_with_indexing_issues": 1,
            "errors": [],
            "issue_groups": [],
            "breakdown": {"high_issues": 1, "medium_issues": 1, "low_issues": 0},
        }
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
                "success": False,
                "source": "fallback",
                "title": "Рекомендации временно недоступны",
                "summary": "Попробуйте позже.",
                "items": [],
                "priority": "medium",
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
        self.assertEqual(result["source"], "ai")
        mocked_post.assert_called_once()

    @patch("core.services.ai_recommendations.requests.post")
    def test_conversion_recommendations_parse_plain_text_response(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={"output_text": "1. Упростите форму.\n2. Добавьте более заметный CTA."},
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
                "cta_funnel": {"rows": [{"cta_id": "hero", "cta_text": "Оставить заявку", "clicks": 3}]},
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
                                "text": '{"title":"AI-рекомендации по SEO","summary":"Проверьте title и скорость.","items":["Исправьте title"],"priority":"high"}',
                            }
                        ],
                    },
                ],
            },
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=11,
            audit_payload={
                "domain": "example.com",
                "score": 55,
                "seo_score": 55,
                "pages_count": 2,
                "has_robots_txt": True,
                "pages_with_speed_issues": 1,
                "pages_with_indexing_issues": 0,
                "errors": [],
                "issue_groups": [],
                "breakdown": {"high_issues": 0, "medium_issues": 1, "low_issues": 0},
            },
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "ai")
        self.assertEqual(result["priority"], "high")
        self.assertGreaterEqual(len(result.get("items") or []), 1)

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_recommendations_return_structured_payload(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={
                "output_text": (
                    '{"title":"AI-рекомендации по SEO","summary":"Есть точки роста по мета-тегам и скорости.",'
                    '"priority":"high",'
                    '"overview":{"seo_score_label":"есть точки роста","pages_checked_label":"достаточно данных",'
                    '"errors_label":"есть критичные ошибки","speed_label":"ниже нормы","indexing_label":"в целом нормально"},'
                    '"highlights":["Просадка связана с title.","Скорость части страниц ниже нормы."],'
                    '"metrics_review":[{"label":"SEO-оценка","value":"61","status":"warning","comment":"Нужны доработки."}],'
                    '"problems":[{"title":"Проблемы с title","severity":"high","description":"На ряде страниц нет title."}],'
                    '"fix_plan":[{"step":1,"title":"Исправить title","details":"Начните с приоритетных страниц."}],'
                    '"recommendations":["Обновите title на страницах с трафиком."]}'
                )
            },
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=12,
            audit_payload={
                "domain": "example.com",
                "score": 61,
                "seo_score": 61,
                "pages_count": 8,
                "has_robots_txt": True,
                "has_sitemap_xml": True,
                "pages_with_speed_issues": 2,
                "pages_with_indexing_issues": 1,
                "errors": [],
                "issue_groups": [],
                "breakdown": {"high_issues": 1, "medium_issues": 2, "low_issues": 1},
            },
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "ai")
        self.assertIn("overview", result)
        self.assertIn("metrics_review", result)
        self.assertIn("problems", result)
        self.assertIn("fix_plan", result)
        self.assertIn("recommendations", result)
        self.assertGreaterEqual(len(result.get("recommendations") or []), 1)
        self.assertEqual(result.get("items"), result.get("recommendations"))

    @patch("core.services.ai_recommendations.requests.post")
    def test_seo_recommendations_plain_text_builds_structured_defaults(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={"output_text": "Сначала исправьте title и canonical на ключевых страницах."},
        )

        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=13,
            audit_payload={
                "domain": "example.com",
                "score": 55,
                "seo_score": 55,
                "pages_count": 4,
                "has_robots_txt": True,
                "has_sitemap_xml": False,
                "pages_with_speed_issues": 1,
                "pages_with_indexing_issues": 2,
                "errors": [],
                "issue_groups": [],
                "breakdown": {"high_issues": 1, "medium_issues": 1, "low_issues": 0},
            },
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "ai")
        self.assertTrue(isinstance(result.get("metrics_review"), list))
        self.assertTrue(isinstance(result.get("fix_plan"), list))
        self.assertTrue(isinstance(result.get("recommendations"), list))
        self.assertGreaterEqual(len(result.get("recommendations") or []), 1)

    @patch(
        "core.services.ai_recommendations.requests.post",
        side_effect=requests.exceptions.ReadTimeout("openai timeout"),
    )
    def test_seo_recommendations_timeout_returns_structured_fallback(self, mocked_post):
        result = get_seo_ai_recommendations(
            client_id=1,
            audit_id=14,
            audit_payload={
                "domain": "example.com",
                "score": 58,
                "seo_score": 58,
                "pages_count": 6,
                "has_robots_txt": True,
                "has_sitemap_xml": True,
                "pages_with_speed_issues": 2,
                "pages_with_indexing_issues": 1,
                "errors": [],
                "issue_groups": [],
                "breakdown": {"high_issues": 1, "medium_issues": 2, "low_issues": 1},
            },
            force_refresh=True,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "fallback")
        self.assertTrue(result.get("fallback"))
        self.assertIn("overview", result)
        self.assertIn("metrics_review", result)
        self.assertGreaterEqual(len(result.get("items") or []), 1)
        self.assertEqual(result.get("items"), result.get("recommendations"))
        self.assertEqual(result.get("debug", {}).get("error_type"), "network_timeout")
        self.assertEqual(mocked_post.call_count, 2)

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
        self.assertEqual(mocked_post.call_count, 2)
