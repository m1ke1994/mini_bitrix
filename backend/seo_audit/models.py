# -*- coding: utf-8 -*-
from django.db import models

from clients.models import Client


class SiteSEOAudit(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "В очереди"
        RUNNING = "running", "Выполняется"
        DONE = "done", "Готово"
        ERROR = "error", "Ошибка"
        STOPPED = "stopped", "Остановлено"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="seo_audits")
    domain = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    seo_score = models.IntegerField(default=0)
    pages_count = models.PositiveIntegerField(default=0)
    used_sitemap = models.BooleanField(default=False)
    sitemap_urls_count = models.PositiveIntegerField(default=0)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"SEO-аудит #{self.pk} {self.domain} ({self.status})"


class SEOPage(models.Model):
    audit = models.ForeignKey(SiteSEOAudit, on_delete=models.CASCADE, related_name="pages")
    url = models.TextField()
    status_code = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=512, blank=True, default="")
    title_length = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, default="")
    description_length = models.PositiveIntegerField(default=0)
    h1 = models.TextField(blank=True, default="")
    h1_count = models.PositiveIntegerField(default=0)
    word_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("url", "id")
        indexes = [
            models.Index(fields=["audit", "url"]),
        ]

    def __str__(self) -> str:
        return f"SEO-страница #{self.pk} ({self.status_code}) {self.url}"


class SEOIssue(models.Model):
    class IssueType(models.TextChoices):
        MISSING_TITLE = "missing_title", "missing_title"
        BAD_TITLE_LENGTH = "bad_title_length", "bad_title_length"
        TITLE_TOO_SHORT = "title_too_short", "title_too_short"
        TITLE_TOO_LONG = "title_too_long", "title_too_long"
        MISSING_DESCRIPTION = "missing_description", "missing_description"
        DESCRIPTION_TOO_SHORT = "description_too_short", "description_too_short"
        DESCRIPTION_TOO_LONG = "description_too_long", "description_too_long"
        DUPLICATE_TITLE = "duplicate_title", "duplicate_title"
        MISSING_H1 = "missing_h1", "missing_h1"
        MULTIPLE_H1 = "multiple_h1", "multiple_h1"
        LONG_H1 = "long_h1", "long_h1"
        HEADING_HIERARCHY_GAP = "heading_hierarchy_gap", "heading_hierarchy_gap"
        LOW_WORD_COUNT = "low_word_count", "low_word_count"
        IMAGE_MISSING_ALT = "image_missing_alt", "image_missing_alt"
        IMAGE_EMPTY_ALT = "image_empty_alt", "image_empty_alt"
        BAD_STATUS = "bad_status", "bad_status"
        NETWORK_ERROR = "network_error", "network_error"
        REDIRECT = "redirect", "redirect"
        SLOW_RESPONSE = "slow_response", "slow_response"
        LARGE_PAGE_SIZE = "large_page_size", "large_page_size"
        MISSING_CANONICAL = "missing_canonical", "missing_canonical"
        MISSING_META_ROBOTS = "missing_meta_robots", "missing_meta_robots"
        MISSING_VIEWPORT = "missing_viewport", "missing_viewport"
        MISSING_CHARSET = "missing_charset", "missing_charset"
        MISSING_ROBOTS_TXT = "missing_robots_txt", "missing_robots_txt"
        ROBOTS_DISALLOW_ALL = "robots_disallow_all", "robots_disallow_all"
        ROBOTS_MISSING_SITEMAP = "robots_missing_sitemap", "robots_missing_sitemap"
        MISSING_SITEMAP = "missing_sitemap", "missing_sitemap"
        BAD_SITEMAP_STATUS = "bad_sitemap_status", "bad_sitemap_status"
        SITEMAP_MISMATCH = "sitemap_mismatch", "sitemap_mismatch"

    class Severity(models.TextChoices):
        LOW = "low", "Низкая"
        MEDIUM = "medium", "Средняя"
        HIGH = "high", "Критичная"

    page = models.ForeignKey(SEOPage, on_delete=models.CASCADE, related_name="issues")
    issue_type = models.CharField(max_length=64, choices=IssueType.choices)
    severity = models.CharField(max_length=16, choices=Severity.choices)
    recommendation = models.TextField()

    class Meta:
        ordering = ("page__url", "id")

    def __str__(self) -> str:
        return f"SEO-ошибка #{self.pk} {self.issue_type} ({self.severity})"
