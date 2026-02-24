from django.db import models

from clients.models import Client


class SiteSEOAudit(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "pending"
        RUNNING = "running", "running"
        DONE = "done", "done"
        ERROR = "error", "error"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="seo_audits")
    domain = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    seo_score = models.IntegerField(default=0)
    pages_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"SEO audit #{self.pk} {self.domain} ({self.status})"


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
        return f"SEO page #{self.pk} ({self.status_code}) {self.url}"


class SEOIssue(models.Model):
    class IssueType(models.TextChoices):
        MISSING_TITLE = "missing_title", "missing_title"
        BAD_TITLE_LENGTH = "bad_title_length", "bad_title_length"
        MISSING_DESCRIPTION = "missing_description", "missing_description"
        DUPLICATE_TITLE = "duplicate_title", "duplicate_title"
        MISSING_H1 = "missing_h1", "missing_h1"
        MULTIPLE_H1 = "multiple_h1", "multiple_h1"
        BAD_STATUS = "bad_status", "bad_status"

    class Severity(models.TextChoices):
        LOW = "low", "low"
        MEDIUM = "medium", "medium"
        HIGH = "high", "high"

    page = models.ForeignKey(SEOPage, on_delete=models.CASCADE, related_name="issues")
    issue_type = models.CharField(max_length=64, choices=IssueType.choices)
    severity = models.CharField(max_length=16, choices=Severity.choices)
    recommendation = models.TextField()

    class Meta:
        ordering = ("page__url", "id")

    def __str__(self) -> str:
        return f"SEO issue #{self.pk} {self.issue_type} ({self.severity})"

