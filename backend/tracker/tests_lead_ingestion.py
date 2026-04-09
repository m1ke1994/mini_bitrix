from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from clients.models import Client
from leads.models import Lead
from tracker.models import Site


class TrackerLeadIngestionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="owner-lead-ingestion",
            email="owner-lead-ingestion@example.com",
            password="pass12345",
        )
        self.client_obj = Client.objects.create(owner=self.user, name="Client with tracker token")
        self.site = Site.objects.create(
            token="site-token-123",
            client=self.client_obj,
            domain="novoe-konakovo.ru",
            is_active=True,
        )
        self.http = APIClient()

    def _send_pageview(self, *, session_id: str, visitor_id: str):
        return self.http.post(
            "/api/track/pageview/",
            {
                "token": self.site.token,
                "session_id": session_id,
                "visitor_id": visitor_id,
                "url": "https://novoe-konakovo.ru/landing?utm_source=yandex&utm_medium=cpc&utm_campaign=spring",
                "title": "Landing",
            },
            format="json",
        )

    def _send_form_success(self, *, session_id: str, visitor_id: str, submission_id: str):
        return self.http.post(
            "/api/track/event/",
            {
                "token": self.site.token,
                "session_id": session_id,
                "visitor_id": visitor_id,
                "type": "form_submit_success",
                "payload": {
                    "submission_id": submission_id,
                    "page_url": "https://novoe-konakovo.ru/landing?utm_source=yandex&utm_medium=cpc&utm_campaign=spring",
                    "referrer": "https://ya.ru/",
                    "utm_source": "yandex",
                    "utm_medium": "cpc",
                    "utm_campaign": "spring",
                    "lead_data": {
                        "name": "Иван",
                        "phone": "+7 (999) 123-45-67",
                        "email": "ivan@example.com",
                        "message": "Нужна консультация",
                    },
                },
            },
            format="json",
        )

    def test_form_submit_success_creates_lead_for_site_token_client(self):
        self._send_pageview(session_id="session-1", visitor_id="visitor-1")
        response = self._send_form_success(session_id="session-1", visitor_id="visitor-1", submission_id="subm-1")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lead.objects.filter(client=self.client_obj).count(), 1)

        lead = Lead.objects.filter(client=self.client_obj).select_related("stage").first()
        self.assertIsNotNone(lead)
        self.assertEqual(lead.tracker_submission_id, "subm-1")
        self.assertEqual(lead.session_id, "session-1")
        self.assertEqual(lead.visitor_id, "visitor-1")
        self.assertEqual(lead.utm_source, "yandex")
        self.assertEqual(lead.utm_medium, "cpc")
        self.assertEqual(lead.utm_campaign, "spring")
        self.assertEqual(lead.email, "ivan@example.com")
        self.assertIsNotNone(lead.stage_id)

    def test_form_submit_success_is_idempotent_by_submission_id(self):
        self._send_pageview(session_id="session-2", visitor_id="visitor-2")

        response_first = self._send_form_success(
            session_id="session-2",
            visitor_id="visitor-2",
            submission_id="subm-dedup-1",
        )
        response_second = self._send_form_success(
            session_id="session-2",
            visitor_id="visitor-2",
            submission_id="subm-dedup-1",
        )

        self.assertEqual(response_first.status_code, 201)
        self.assertEqual(response_second.status_code, 201)
        self.assertEqual(Lead.objects.filter(client=self.client_obj).count(), 1)
