from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from analytics_app.views import _build_ai_event_signals_payload
from clients.models import Client
from tracker.models import Event as TrackerEvent
from tracker.models import Site, Visit


class AiSignalsPayloadTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass12345",
        )
        self.client_obj = Client.objects.create(owner=self.user, name="AI Signal Client")
        self.site = Site.objects.create(token=self.client_obj.api_key, domain="test.local", is_active=True)
        self.visit = Visit.objects.create(
            site=self.site,
            session_id="session-ai-payload",
            visitor_id="visitor-ai-payload",
            started_at=timezone.now(),
        )

    def test_ai_signal_payload_aggregates_stage_one_events(self):
        now = timezone.now()
        TrackerEvent.objects.bulk_create(
            [
                TrackerEvent(
                    visit=self.visit,
                    type="scroll_depth",
                    payload={"depth": 25},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="scroll_depth",
                    payload={"depth": 80},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="form_view",
                    payload={},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="form_start",
                    payload={},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="form_first_field_filled",
                    payload={},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="form_submit_attempt",
                    payload={},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="form_submit_success",
                    payload={},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="form_submit_error",
                    payload={},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="section_view",
                    payload={"section_key": "hero"},
                    timestamp=now,
                ),
                TrackerEvent(
                    visit=self.visit,
                    type="cta_click",
                    payload={"cta_key": "hero_cta"},
                    timestamp=now,
                ),
            ]
        )

        payload = _build_ai_event_signals_payload(
            client=self.client_obj,
            from_dt=now - timedelta(days=1),
            to_dt=now + timedelta(days=1),
        )

        self.assertEqual(payload["scroll_depth"]["events_total"], 2)
        self.assertEqual(payload["scroll_depth"]["thresholds"]["25"], 1)
        self.assertEqual(payload["scroll_depth"]["thresholds"]["75"], 1)
        self.assertEqual(payload["forms"]["form_view"], 1)
        self.assertEqual(payload["forms"]["form_start"], 1)
        self.assertEqual(payload["forms"]["form_first_field_filled"], 1)
        self.assertEqual(payload["forms"]["form_submit_attempt"], 1)
        self.assertEqual(payload["forms"]["form_submit_success"], 1)
        self.assertEqual(payload["forms"]["form_submit_error"], 1)
        self.assertEqual(payload["section_views"]["events_total"], 1)
        self.assertEqual(payload["cta_clicks"]["events_total"], 1)
