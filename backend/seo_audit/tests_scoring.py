# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase

from clients.models import Client
from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit
from seo_audit.services.scoring import recalculate_audit_score


class SEOScoreCalculationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="seo-score-owner",
            email="seo-score-owner@example.com",
            password="pass12345",
        )
        self.client_obj = Client.objects.create(owner=self.user, name="SEO Score Client")

    def test_score_drops_for_unavailable_site_without_robots_and_sitemap(self):
        audit = SiteSEOAudit.objects.create(
            client=self.client_obj,
            domain="broken.example.com",
            has_robots_txt=False,
            has_sitemap_xml=False,
            sitemap_urls_count=0,
        )
        page = SEOPage.objects.create(
            audit=audit,
            url="https://broken.example.com/",
            status_code=0,
            ttfb_ms=4200,
            performance_score=0,
            speed_status=SEOPage.SpeedStatus.CRITICAL,
            indexability_status=SEOPage.IndexabilityStatus.UNKNOWN,
            title="",
            description="",
            h1="",
            h1_count=0,
            canonical_url="",
            in_sitemap=False,
            blocked_by_robots=False,
        )
        SEOIssue.objects.create(page=page, issue_type="network_error", severity=SEOIssue.Severity.HIGH, recommendation="-")
        SEOIssue.objects.create(page=page, issue_type="missing_robots_txt", severity=SEOIssue.Severity.LOW, recommendation="-")
        SEOIssue.objects.create(page=page, issue_type="missing_sitemap", severity=SEOIssue.Severity.MEDIUM, recommendation="-")
        SEOIssue.objects.create(page=page, issue_type="slow_ttfb", severity=SEOIssue.Severity.HIGH, recommendation="-")

        recalculate_audit_score(audit)
        audit.refresh_from_db()

        self.assertLessEqual(audit.seo_score, 35)
        self.assertEqual(audit.pages_count, 1)
        self.assertGreaterEqual(audit.pages_with_speed_issues, 1)
        self.assertGreaterEqual(audit.pages_with_indexing_issues, 1)

    def test_score_remains_high_for_technically_healthy_pages(self):
        audit = SiteSEOAudit.objects.create(
            client=self.client_obj,
            domain="healthy.example.com",
            has_robots_txt=True,
            has_sitemap_xml=True,
            sitemap_urls_count=2,
        )
        SEOPage.objects.create(
            audit=audit,
            url="https://healthy.example.com/",
            status_code=200,
            ttfb_ms=280,
            performance_score=92,
            speed_status=SEOPage.SpeedStatus.GOOD,
            indexability_status=SEOPage.IndexabilityStatus.INDEXABLE,
            title="Healthy Example Home",
            description="Detailed description for search snippets and result quality checks.",
            h1="Home page",
            h1_count=1,
            word_count=520,
            canonical_url="https://healthy.example.com/",
            in_sitemap=True,
            blocked_by_robots=False,
        )
        SEOPage.objects.create(
            audit=audit,
            url="https://healthy.example.com/about",
            status_code=200,
            ttfb_ms=360,
            performance_score=87,
            speed_status=SEOPage.SpeedStatus.GOOD,
            indexability_status=SEOPage.IndexabilityStatus.INDEXABLE,
            title="About Healthy Example Company",
            description="Company page with contacts, key benefits and additional useful details.",
            h1="About company",
            h1_count=1,
            word_count=610,
            canonical_url="https://healthy.example.com/about",
            in_sitemap=True,
            blocked_by_robots=False,
        )

        recalculate_audit_score(audit)
        audit.refresh_from_db()

        self.assertGreaterEqual(audit.seo_score, 80)
        self.assertEqual(audit.pages_count, 2)
        self.assertEqual(audit.pages_with_speed_issues, 0)
        self.assertEqual(audit.pages_with_indexing_issues, 0)
