# -*- coding: utf-8 -*-
from datetime import date
from unittest.mock import patch

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
        self.assertNotIn("temperature", body)

    @patch("core.services.ai_recommendations.requests.post")
    def test_request_openai_keeps_temperature_for_non_gpt5_models(self, mocked_post):
        mocked_post.return_value = _mock_response(
            status_code=200,
            payload={"output_text": '{"title":"x","summary":"y","items":["z"],"priority":"high"}'},
        )

        _request_openai(model="gpt-4.1-mini", system_prompt="system", user_prompt="user")

        body = mocked_post.call_args.kwargs["json"]
        self.assertEqual(body.get("temperature"), 0.2)

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
