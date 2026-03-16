# -*- coding: utf-8 -*-
import csv
import logging
from io import StringIO

from celery.result import AsyncResult
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import permissions, renderers, status
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit
from seo_audit.serializers import SEOAuditStartSerializer, SEOIssueSerializer, SEOPageSerializer, SiteSEOAuditSerializer
from seo_audit.services.scoring import (
    build_audit_comparison,
    build_commercial_summary,
    build_fix_plan,
    build_issue_groups,
    calculate_audit_score_breakdown,
)
from subscriptions.permissions import HasActiveSubscription

logger = logging.getLogger(__name__)


class CSVRenderer(renderers.BaseRenderer):
    media_type = "text/csv"
    format = "csv"
    charset = "utf-8"
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return b""
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode(self.charset)
        return str(data).encode(self.charset)


def json_response(data, http_status: int):
    return JsonResponse(
        data,
        status=http_status,
        safe=isinstance(data, dict),
        json_dumps_params={"ensure_ascii": False},
    )


def _audit_history_queryset(*, client, domain: str, exclude_audit_id: int | None = None):
    qs = SiteSEOAudit.objects.filter(client=client, domain=domain, status=SiteSEOAudit.Status.DONE).order_by("-created_at")
    if exclude_audit_id:
        qs = qs.exclude(id=exclude_audit_id)
    return qs


def _serialize_history_item(audit: SiteSEOAudit) -> dict:
    breakdown = calculate_audit_score_breakdown(audit)
    return {
        "audit_id": audit.id,
        "domain": audit.domain,
        "status": audit.status,
        "score": int(audit.seo_score or 0),
        "seo_score": int(audit.seo_score or 0),
        "created_at": audit.created_at,
        "finished_at": audit.finished_at,
        "pages_count": int(audit.pages_count or 0),
        "high_issues": int(breakdown["high_issues"]),
        "medium_issues": int(breakdown["medium_issues"]),
        "low_issues": int(breakdown["low_issues"]),
        "pages_with_speed_issues": int(audit.pages_with_speed_issues or 0),
        "pages_with_indexing_issues": int(audit.pages_with_indexing_issues or 0),
    }


def _build_comparison_or_stub(*, current_audit: SiteSEOAudit, previous_audit: SiteSEOAudit | None) -> dict:
    if current_audit.status != SiteSEOAudit.Status.DONE:
        return {
            "has_data": False,
            "reason": "Сравнение доступно после завершения текущего аудита.",
        }
    if not previous_audit:
        return {
            "has_data": False,
            "reason": "Для выбранного домена пока нет предыдущего завершённого аудита.",
        }
    return build_audit_comparison(current_audit=current_audit, previous_audit=previous_audit)


def _safe_audit_payload(audit: SiteSEOAudit) -> dict:
    try:
        return SiteSEOAuditSerializer(audit).data
    except Exception:
        logger.exception("seo_audit.detail failed to serialize audit_id=%s", audit.id)
        return {
            "id": audit.id,
            "domain": audit.domain,
            "status": audit.status,
            "score": int(audit.seo_score or 0),
            "seo_score": int(audit.seo_score or 0),
            "pages_count": int(audit.pages_count or 0),
            "used_sitemap": bool(getattr(audit, "used_sitemap", False)),
            "sitemap_urls_count": int(getattr(audit, "sitemap_urls_count", 0) or 0),
            "pages_with_speed_issues": int(getattr(audit, "pages_with_speed_issues", 0) or 0),
            "pages_with_indexing_issues": int(getattr(audit, "pages_with_indexing_issues", 0) or 0),
            "has_robots_txt": bool(getattr(audit, "has_robots_txt", False)),
            "has_sitemap_xml": bool(getattr(audit, "has_sitemap_xml", False)),
            "avg_ttfb_ms": int(getattr(audit, "avg_ttfb_ms", 0) or 0),
            "avg_performance_score": int(getattr(audit, "avg_performance_score", 0) or 0),
            "created_at": audit.created_at,
            "finished_at": audit.finished_at,
        }


def _build_audit_detail_payload(*, audit: SiteSEOAudit, client) -> dict:
    try:
        pages = list(audit.pages.all() or [])
    except Exception:
        logger.exception("seo_audit.detail failed to fetch pages audit_id=%s", audit.id)
        pages = []

    try:
        issues = list(
            SEOIssue.objects.filter(page__audit=audit)
            .select_related("page")
            .order_by("page__url", "id")
        )
    except Exception:
        logger.exception("seo_audit.detail failed to fetch issues audit_id=%s", audit.id)
        issues = []

    audit_payload = _safe_audit_payload(audit)

    try:
        pages_payload = SEOPageSerializer(pages, many=True).data if pages else []
    except Exception:
        logger.exception("seo_audit.detail failed to serialize pages audit_id=%s", audit.id)
        pages_payload = []

    try:
        issues_payload = SEOIssueSerializer(issues, many=True).data if issues else []
    except Exception:
        logger.exception("seo_audit.detail failed to serialize issues audit_id=%s", audit.id)
        issues_payload = []

    grouped_errors = {"high": [], "medium": [], "low": []}
    for item in issues_payload:
        severity = str(item.get("severity") or "").lower()
        if severity in grouped_errors:
            grouped_errors[severity].append(item)

    breakdown = {
        "score": int(audit_payload.get("score", audit.seo_score or 0) or 0),
        "high_issues": len(grouped_errors["high"]),
        "medium_issues": len(grouped_errors["medium"]),
        "low_issues": len(grouped_errors["low"]),
    }

    issue_groups = build_issue_groups(issues_payload)
    commercial_summary = build_commercial_summary(pages_payload)
    pages_payload = commercial_summary.get("pages", pages_payload)
    fix_plan = build_fix_plan(audit=audit, issue_groups=issue_groups, commercial_summary=commercial_summary)

    history_audits = list(_audit_history_queryset(client=client, domain=audit.domain, exclude_audit_id=audit.id)[:10])
    history_items = [_serialize_history_item(item) for item in history_audits]
    previous_done_audit = history_audits[0] if history_audits else None
    comparison_preview = _build_comparison_or_stub(current_audit=audit, previous_audit=previous_done_audit)

    payload = {
        "id": audit_payload.get("id", audit.id),
        "domain": audit_payload.get("domain", audit.domain),
        "status": audit_payload.get("status", audit.status),
        "score": int(audit_payload.get("score", audit.seo_score or 0) or 0),
        "seo_score": int(audit_payload.get("seo_score", audit.seo_score or 0) or 0),
        "pages_count": int(audit_payload.get("pages_count", 0) or 0),
        "used_sitemap": bool(audit_payload.get("used_sitemap", getattr(audit, "used_sitemap", False))),
        "sitemap_urls_count": int(audit_payload.get("sitemap_urls_count", getattr(audit, "sitemap_urls_count", 0)) or 0),
        "pages_with_speed_issues": int(
            audit_payload.get("pages_with_speed_issues", getattr(audit, "pages_with_speed_issues", 0)) or 0
        ),
        "pages_with_indexing_issues": int(
            audit_payload.get("pages_with_indexing_issues", getattr(audit, "pages_with_indexing_issues", 0)) or 0
        ),
        "has_robots_txt": bool(audit_payload.get("has_robots_txt", getattr(audit, "has_robots_txt", False))),
        "has_sitemap_xml": bool(audit_payload.get("has_sitemap_xml", getattr(audit, "has_sitemap_xml", False))),
        "avg_ttfb_ms": int(audit_payload.get("avg_ttfb_ms", getattr(audit, "avg_ttfb_ms", 0)) or 0),
        "avg_performance_score": int(
            audit_payload.get("avg_performance_score", getattr(audit, "avg_performance_score", 0)) or 0
        ),
        "created_at": audit_payload.get("created_at", audit.created_at),
        "pages": pages_payload,
        "errors": issues_payload,
        "grouped_errors": grouped_errors,
        "breakdown": breakdown,
        "fix_plan": fix_plan,
        "issue_groups": issue_groups,
        "commercial_summary": commercial_summary,
        "audit_history": history_items,
        "comparison_preview": comparison_preview,
    }
    if not (audit.status == SiteSEOAudit.Status.RUNNING and audit.finished_at is None):
        payload["finished_at"] = audit_payload.get("finished_at", audit.finished_at)

    return payload


def _csv_response(filename: str, rows: list[list]):
    buffer = StringIO()
    writer = csv.writer(buffer)
    for row in rows:
        writer.writerow(row)
    payload = buffer.getvalue()
    response = HttpResponse(payload, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


class SEOAuditStartView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def post(self, request):
        serializer = SEOAuditStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        audit = SiteSEOAudit.objects.create(
            client=request.client,
            domain=serializer.validated_data["domain"],
            status=SiteSEOAudit.Status.PENDING,
        )
        from seo_audit.tasks import run_site_audit_task

        run_site_audit_task.delay(audit.id)
        logger.info("seo_audit.start created audit_id=%s client_id=%s domain=%s", audit.id, request.client.id, audit.domain)
        return json_response(
            {
                "ok": True,
                "audit_id": audit.id,
                "status": audit.status,
                "domain": audit.domain,
            },
            http_status=status.HTTP_201_CREATED,
        )


class SEOAuditLatestView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request):
        domain = str(request.query_params.get("domain") or "").strip().lower()
        audits_qs = SiteSEOAudit.objects.filter(client=request.client)
        if domain:
            audits_qs = audits_qs.filter(domain=domain)
        audit = audits_qs.order_by("-created_at").first()
        if not audit:
            return json_response(
                {
                    "ok": True,
                    "audit_id": None,
                    "domain": domain or None,
                },
                http_status=status.HTTP_200_OK,
            )

        return json_response(
            {
                "ok": True,
                "audit_id": audit.id,
                "domain": audit.domain,
                "status": audit.status,
                "created_at": audit.created_at,
                "finished_at": audit.finished_at,
            },
            http_status=status.HTTP_200_OK,
        )


class SEOAuditDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request, audit_id: int):
        try:
            audit = (
                SiteSEOAudit.objects.filter(id=audit_id, client=request.client)
                .prefetch_related(Prefetch("pages", queryset=SEOPage.objects.order_by("url", "id")))
                .first()
            )
            if not audit:
                return json_response({"detail": "Аудит не найден.", "ok": False}, http_status=status.HTTP_404_NOT_FOUND)

            response = _build_audit_detail_payload(audit=audit, client=request.client)
            logger.info(
                "seo_audit.detail audit_id=%s client_id=%s status=%s score=%s pages=%s issues=%s",
                audit.id,
                request.client.id,
                audit.status,
                audit.seo_score,
                len(response.get("pages") or []),
                len(response.get("errors") or []),
            )
            return json_response(response, http_status=status.HTTP_200_OK)
        except Exception:
            logger.exception("seo_audit.detail error audit_id=%s client_id=%s", audit_id, getattr(request.client, "id", None))
            return json_response({"detail": "Внутренняя ошибка сервера.", "ok": False}, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SEOAuditHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request, audit_id: int):
        audit = SiteSEOAudit.objects.filter(id=audit_id, client=request.client).first()
        if not audit:
            return json_response({"detail": "Аудит не найден.", "ok": False}, http_status=status.HTTP_404_NOT_FOUND)

        history_qs = _audit_history_queryset(client=request.client, domain=audit.domain, exclude_audit_id=audit.id)
        history_rows = [_serialize_history_item(item) for item in list(history_qs[:20])]
        default_compare_audit_id = history_rows[0]["audit_id"] if history_rows else None
        return json_response(
            {
                "ok": True,
                "audit_id": audit.id,
                "domain": audit.domain,
                "rows": history_rows,
                "default_compare_audit_id": default_compare_audit_id,
            },
            http_status=status.HTTP_200_OK,
        )


class SEOAuditCompareView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def get(self, request, audit_id: int):
        current_audit = SiteSEOAudit.objects.filter(id=audit_id, client=request.client).first()
        if not current_audit:
            return json_response({"detail": "Аудит не найден.", "ok": False}, http_status=status.HTTP_404_NOT_FOUND)

        with_audit_id = request.query_params.get("with_audit_id")
        previous_audit = None
        if with_audit_id:
            previous_audit = SiteSEOAudit.objects.filter(
                id=with_audit_id,
                client=request.client,
                domain=current_audit.domain,
                status=SiteSEOAudit.Status.DONE,
            ).first()
        else:
            previous_audit = _audit_history_queryset(
                client=request.client,
                domain=current_audit.domain,
                exclude_audit_id=current_audit.id,
            ).first()

        payload = _build_comparison_or_stub(current_audit=current_audit, previous_audit=previous_audit)
        payload["ok"] = True
        payload["audit_id"] = current_audit.id
        payload["domain"] = current_audit.domain
        if previous_audit:
            payload["with_audit_id"] = previous_audit.id
        return json_response(payload, http_status=status.HTTP_200_OK)


class SEOAuditExportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]
    renderer_classes = [CSVRenderer, renderers.JSONRenderer]

    def get(self, request, audit_id: int):
        audit = SiteSEOAudit.objects.filter(id=audit_id, client=request.client).first()
        if not audit:
            return json_response({"detail": "Аудит не найден.", "ok": False}, http_status=status.HTTP_404_NOT_FOUND)

        detail_payload = _build_audit_detail_payload(audit=audit, client=request.client)
        compare_with_id = request.query_params.get("with_audit_id")
        previous_audit = None
        if compare_with_id:
            previous_audit = SiteSEOAudit.objects.filter(
                id=compare_with_id,
                client=request.client,
                domain=audit.domain,
                status=SiteSEOAudit.Status.DONE,
            ).first()
        else:
            previous_audit = _audit_history_queryset(
                client=request.client,
                domain=audit.domain,
                exclude_audit_id=audit.id,
            ).first()
        comparison = _build_comparison_or_stub(current_audit=audit, previous_audit=previous_audit)

        rows: list[list] = []
        rows.append(["section", "key", "value", "extra_1", "extra_2", "extra_3"])
        rows.append(["summary", "audit_id", detail_payload.get("id"), "", "", ""])
        rows.append(["summary", "domain", detail_payload.get("domain"), "", "", ""])
        rows.append(["summary", "status", detail_payload.get("status"), "", "", ""])
        rows.append(["summary", "score", int(detail_payload.get("score") or 0), "", "", ""])
        rows.append(["summary", "pages_count", int(detail_payload.get("pages_count") or 0), "", "", ""])

        for item in detail_payload.get("fix_plan") or []:
            rows.append(
                [
                    "fix_plan",
                    item.get("title"),
                    item.get("why_it_matters"),
                    item.get("priority_label"),
                    int(item.get("pages_affected") or 0),
                    item.get("target_block"),
                ]
            )

        for item in detail_payload.get("issue_groups") or []:
            rows.append(
                [
                    "issue_groups",
                    item.get("title"),
                    item.get("description"),
                    item.get("severity"),
                    int(item.get("pages_affected") or 0),
                    item.get("target_block"),
                ]
            )

        for page in detail_payload.get("commercial_summary", {}).get("pages") or []:
            rows.append(
                [
                    "commercial_pages",
                    page.get("url"),
                    page.get("commercial_status_label"),
                    int(page.get("commercial_readiness_score") or 0),
                    " | ".join(page.get("commercial_recommendations") or []),
                    "",
                ]
            )

        for issue in detail_payload.get("errors") or []:
            rows.append(
                [
                    "issues",
                    issue.get("page_url"),
                    issue.get("issue_title"),
                    issue.get("severity"),
                    issue.get("issue_type"),
                    issue.get("recommendation"),
                ]
            )

        for page in detail_payload.get("pages") or []:
            rows.append(
                [
                    "pages",
                    page.get("url"),
                    int(page.get("status_code") or 0),
                    int(page.get("ttfb_ms") or 0),
                    int(page.get("performance_score") or 0),
                    page.get("indexability_status"),
                ]
            )

        if comparison.get("has_data"):
            rows.append(
                [
                    "comparison",
                    "trend",
                    comparison.get("trend_label"),
                    comparison.get("score", {}).get("before"),
                    comparison.get("score", {}).get("after"),
                    comparison.get("score", {}).get("delta"),
                ]
            )
            rows.append(
                [
                    "comparison",
                    "new_issues_count",
                    comparison.get("new_issues_count"),
                    "fixed_issues_count",
                    comparison.get("fixed_issues_count"),
                    "",
                ]
            )
        else:
            rows.append(["comparison", "status", "Недостаточно данных для сравнения", "", "", ""])

        safe_domain = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in (audit.domain or "site")).strip("-")
        date_part = timezone.now().date().isoformat()
        filename = f"seo-audit-{safe_domain or 'site'}-{date_part}.csv"
        return _csv_response(filename, rows)


class SEOAuditStopView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def post(self, request, audit_id: int):
        try:
            audit = SiteSEOAudit.objects.filter(id=audit_id, client=request.client).first()
            if not audit:
                return json_response({"detail": "Аудит не найден.", "ok": False}, http_status=status.HTTP_404_NOT_FOUND)

            audit.is_cancelled = True
            update_fields = ["is_cancelled"]
            if audit.status in (SiteSEOAudit.Status.PENDING, SiteSEOAudit.Status.RUNNING):
                audit.status = SiteSEOAudit.Status.STOPPED
                if audit.finished_at is None:
                    audit.finished_at = timezone.now()
                update_fields.extend(["status", "finished_at"])
            audit.save(update_fields=update_fields)

            if audit.celery_task_id:
                try:
                    AsyncResult(audit.celery_task_id).revoke(terminate=False)
                except Exception:
                    logger.exception(
                        "seo_audit.stop failed to revoke audit_id=%s task_id=%s",
                        audit.id,
                        audit.celery_task_id,
                    )

            return json_response(
                {
                    "ok": True,
                    "audit_id": audit.id,
                    "status": audit.status,
                    "finished_at": audit.finished_at,
                },
                http_status=status.HTTP_200_OK,
            )
        except Exception:
            logger.exception("seo_audit.stop error audit_id=%s client_id=%s", audit_id, getattr(request.client, "id", None))
            return json_response({"detail": "Внутренняя ошибка сервера.", "ok": False}, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
