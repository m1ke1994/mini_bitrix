# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from clients.models import Client
from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit
from seo_audit.services.crawler import crawl_site_audit


class _FakeResponse:
    def __init__(self, url, status_code=200, text="", headers=None, apparent_encoding="utf-8", history=None):
        self.url = url
        self.status_code = status_code
        self.text = text
        self.headers = headers or {"Content-Type": "text/html; charset=utf-8"}
        self.apparent_encoding = apparent_encoding
        self.encoding = None
        self.history = history or []
        self.content = str(text or "").encode("utf-8")


class SEOCrawlerServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="seo-owner", email="seo-owner@example.com", password="pass12345")
        self.client_obj = Client.objects.create(owner=self.user, name="SEO Client")

    def test_crawler_creates_pages_and_issues(self):
        audit = SiteSEOAudit.objects.create(client=self.client_obj, domain="example.com")

        pages = {
            "https://example.com/": _FakeResponse(
                url="https://example.com/",
                text="""
                <html>
                  <head>
                    <title>Home page title for SEO checks</title>
                    <meta name="description" content="Main page description text">
                  </head>
                  <body>
                    <h1>Home</h1>
                    <p>Welcome to the home page.</p>
                    <a href="/about">About</a>
                    <a href="https://external.example.org/">External</a>
                  </body>
                </html>
                """,
            ),
            "https://example.com/about": _FakeResponse(
                url="https://example.com/about",
                text="""
                <html>
                  <head>
                    <title>Short</title>
                  </head>
                  <body>
                    <h1>About</h1>
                    <h1>Second heading</h1>
                    <p>About page text content.</p>
                    <a href="/missing">Broken page</a>
                  </body>
                </html>
                """,
            ),
            "https://example.com/missing": _FakeResponse(
                url="https://example.com/missing",
                status_code=404,
                text="<html><head></head><body><p>Not found</p></body></html>",
            ),
            "https://example.com/robots.txt": _FakeResponse(
                url="https://example.com/robots.txt",
                headers={"Content-Type": "text/plain; charset=utf-8"},
                text="User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml\n",
            ),
            "https://example.com/sitemap.xml": _FakeResponse(
                url="https://example.com/sitemap.xml",
                headers={"Content-Type": "application/xml; charset=utf-8"},
                text="""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                  <url><loc>https://example.com/</loc></url>
                  <url><loc>https://example.com/about</loc></url>
                  <url><loc>https://example.com/missing?utm=ad#top</loc></url>
                </urlset>
                """,
            ),
        }

        def fake_get(*args, **kwargs):
            url = args[0] if args else kwargs.get("url")
            if url is None and len(args) >= 2:
                url = args[1]
            normalized = str(url).rstrip("/") or str(url)
            if str(url) == "https://example.com/":
                normalized = "https://example.com/"
            if normalized not in pages:
                raise AssertionError(f"Unexpected URL requested: {url}")
            return pages[normalized]

        with patch("seo_audit.services.crawler.requests.Session.get", side_effect=fake_get):
            crawl_site_audit(audit)

        audit.refresh_from_db()
        self.assertEqual(audit.status, SiteSEOAudit.Status.PENDING)
        self.assertTrue(audit.used_sitemap)
        self.assertEqual(audit.sitemap_urls_count, 3)
        self.assertGreaterEqual(audit.pages_count, 2)
        self.assertTrue(SEOPage.objects.filter(audit=audit, url="https://example.com/about").exists())
        self.assertGreater(SEOIssue.objects.filter(page__audit=audit).count(), 0)
        self.assertTrue(SEOIssue.objects.filter(page__audit=audit, issue_type="missing_description").exists())
        self.assertTrue(SEOIssue.objects.filter(page__audit=audit, issue_type="multiple_h1").exists())
        self.assertTrue(SEOIssue.objects.filter(page__audit=audit, issue_type="bad_status").exists())
