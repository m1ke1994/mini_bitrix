# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from rest_framework import serializers

from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit
from seo_audit.services.messages import get_issue_title


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
    class Meta:
        model = SEOPage
        fields = (
            "id",
            "url",
            "status_code",
            "title",
            "title_length",
            "description",
            "description_length",
            "h1",
            "h1_count",
            "word_count",
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
            "created_at",
            "finished_at",
        )
