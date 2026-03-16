# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from rest_framework import serializers

from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit
from seo_audit.services.messages import get_commercial_recommendations, get_commercial_status_label, get_issue_title


class SEOAuditStartSerializer(serializers.Serializer):
    domain = serializers.CharField(max_length=255)

    def validate_domain(self, value):
        raw = (value or "").strip()
        if not raw:
            raise serializers.ValidationError("Укажите домен.")
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
        hostname = (parsed.hostname or "").strip().lower()
        if not hostname:
            raise serializers.ValidationError("Некорректный домен.")
        return hostname


class SEOPageSerializer(serializers.ModelSerializer):
    commercial_signals = serializers.SerializerMethodField()
    commercial_recommendations = serializers.SerializerMethodField()
    commercial_status_label = serializers.SerializerMethodField()

    def get_commercial_signals(self, obj):
        return {
            "has_form": bool(getattr(obj, "has_form", False)),
            "has_cta": bool(getattr(obj, "has_cta", False)),
            "has_phone_or_contact": bool(getattr(obj, "has_phone_or_contact", False)),
            "has_messenger": bool(getattr(obj, "has_messenger", False)),
            "has_offer_like_heading": bool(getattr(obj, "has_offer_like_heading", False)),
            "has_benefits_block": bool(getattr(obj, "has_benefits_block", False)),
            "has_faq": bool(getattr(obj, "has_faq", False)),
        }

    def get_commercial_recommendations(self, obj):
        return get_commercial_recommendations(self.get_commercial_signals(obj))

    def get_commercial_status_label(self, obj):
        return get_commercial_status_label(getattr(obj, "commercial_status", "warning"))

    class Meta:
        model = SEOPage
        fields = (
            "id",
            "url",
            "status_code",
            "ttfb_ms",
            "html_size_bytes",
            "js_files_count",
            "css_files_count",
            "images_count",
            "total_js_bytes",
            "total_css_bytes",
            "total_image_bytes",
            "performance_score",
            "speed_status",
            "title",
            "title_length",
            "description",
            "description_length",
            "h1",
            "h1_count",
            "word_count",
            "meta_robots",
            "canonical_url",
            "indexability_status",
            "in_sitemap",
            "blocked_by_robots",
            "has_form",
            "has_cta",
            "has_phone_or_contact",
            "has_messenger",
            "has_offer_like_heading",
            "has_benefits_block",
            "has_faq",
            "commercial_readiness_score",
            "commercial_status",
            "commercial_status_label",
            "commercial_signals",
            "commercial_recommendations",
        )


class SEOIssueSerializer(serializers.ModelSerializer):
    page_id = serializers.IntegerField(read_only=True)
    page_url = serializers.CharField(source="page.url", read_only=True)
    issue_title = serializers.SerializerMethodField()

    def get_issue_title(self, obj):
        return get_issue_title(obj.issue_type)

    class Meta:
        model = SEOIssue
        fields = ("id", "page_id", "page_url", "issue_type", "issue_title", "severity", "recommendation")


class SiteSEOAuditSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(source="seo_score", read_only=True)

    class Meta:
        model = SiteSEOAudit
        fields = (
            "id",
            "domain",
            "status",
            "score",
            "seo_score",
            "pages_count",
            "used_sitemap",
            "sitemap_urls_count",
            "pages_with_speed_issues",
            "pages_with_indexing_issues",
            "has_robots_txt",
            "has_sitemap_xml",
            "avg_ttfb_ms",
            "avg_performance_score",
            "created_at",
            "finished_at",
        )
