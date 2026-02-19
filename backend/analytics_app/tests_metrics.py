from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from analytics_app.models import Event
from analytics_app.services.metrics import get_metrics
from clients.models import Client
from leads.models import Lead
from tracker.models import Site, Visit


class MetricsServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="owner", email="owner@example.com", password="pass12345")
        self.client_obj = Client.objects.create(owner=self.user, name="Test Client")
        self.site = Site.objects.create(token=self.client_obj.api_key, domain="test.local", is_active=True)
        self.date_to = timezone.localdate()
        self.date_from = self.date_to - timedelta(days=1)

    def _visit(self, session_id, visitor_id):
        Visit.objects.create(
            site=self.site,
            session_id=session_id,
            visitor_id=visitor_id,
            started_at=timezone.now(),
        )

    def test_single_visitor_multiple_visits(self):
        for idx in range(8):
            self._visit(session_id=f"session-{idx}", visitor_id="visitor-1")

        metrics = get_metrics(self.client_obj, self.date_from, self.date_to)
        self.assertEqual(metrics["visits"], 8)
        self.assertEqual(metrics["unique_users"], 1)

    def test_two_visitors_total_eight_visits(self):
        for idx in range(5):
            self._visit(session_id=f"session-a-{idx}", visitor_id="visitor-a")
        for idx in range(3):
            self._visit(session_id=f"session-b-{idx}", visitor_id="visitor-b")

        metrics = get_metrics(self.client_obj, self.date_from, self.date_to)
        self.assertEqual(metrics["visits"], 8)
        self.assertEqual(metrics["unique_users"], 2)

    def test_conversion_and_legacy_missing_visitor_id(self):
        for idx in range(2):
            self._visit(session_id=f"legacy-{idx}", visitor_id="")
        Event.objects.create(
            client=self.client_obj,
            visitor_id="",
            event_type=Event.EventType.FORM_SUBMIT,
            element_id="contact-form",
            page_url="https://test.local/",
        )
        Lead.objects.create(client=self.client_obj, name="Lead One")

        metrics = get_metrics(self.client_obj, self.date_from, self.date_to)
        self.assertEqual(metrics["visits"], 2)
        self.assertEqual(metrics["unique_users"], 2)
        self.assertEqual(metrics["forms"], 1)
        self.assertEqual(metrics["leads"], 1)
        self.assertEqual(metrics["conversion"], 50.0)

    def test_conversion_uses_form_submit_when_leads_absent(self):
        for idx in range(5):
            self._visit(session_id=f"session-{idx}", visitor_id=f"visitor-{idx}")
        for idx in range(2):
            Event.objects.create(
                client=self.client_obj,
                visitor_id=f"visitor-{idx}",
                event_type=Event.EventType.FORM_SUBMIT,
                element_id=f"form-{idx}",
                page_url="https://test.local/contact",
            )

        metrics = get_metrics(self.client_obj, self.date_from, self.date_to)
        self.assertEqual(metrics["visits"], 5)
        self.assertEqual(metrics["forms"], 2)
        self.assertEqual(metrics["leads"], 0)
        self.assertEqual(metrics["conversion"], 40.0)

    def test_conversion_falls_back_to_leads_when_forms_absent(self):
        for idx in range(4):
            self._visit(session_id=f"session-{idx}", visitor_id=f"visitor-{idx}")
        for idx in range(2):
            Lead.objects.create(client=self.client_obj, name=f"Lead {idx + 1}")

        metrics = get_metrics(self.client_obj, self.date_from, self.date_to)
        self.assertEqual(metrics["visits"], 4)
        self.assertEqual(metrics["forms"], 0)
        self.assertEqual(metrics["leads"], 2)
        self.assertEqual(metrics["conversion"], 50.0)
