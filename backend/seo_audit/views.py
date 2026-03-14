# -*- coding: utf-8 -*-
import logging

from celery.result import AsyncResult
from django.db.models import Prefetch
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit
from seo_audit.serializers import SEOAuditStartSerializer, SEOIssueSerializer, SEOPageSerializer, SiteSEOAuditSerializer
from subscriptions.permissions import HasActiveSubscription

logger = logging.getLogger(__name__)


def json_response(data, http_status: int):
    return JsonResponse(
        data,
        status=http_status,
        safe=isinstance(data, dict),
        json_dumps_params={"ensure_ascii": False},
    )


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
        logger.info("seo_audit.start создан audit_id=%s client_id=%s domain=%s", audit.id, request.client.id, audit.domain)
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
            logger.info(
                "seo_audit.latest no_audits_found client_id=%s domain=%s",
                request.client.id,
                domain or "<any>",
            )
            return json_response(
                {
                    "ok": True,
                    "audit_id": None,
                    "domain": domain or None,
                },
                http_status=status.HTTP_200_OK,
            )

        logger.info(
            "seo_audit.latest client_id=%s domain=%s audit_id=%s status=%s",
            request.client.id,
            domain or "<any>",
            audit.id,
            audit.status,
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
                .prefetch_related(
                    Prefetch("pages", queryset=SEOPage.objects.order_by("url", "id")),
                )
                .first()
            )
            if not audit:
                return json_response({"detail": "Аудит не найден.", "ok": False}, http_status=status.HTTP_404_NOT_FOUND)

            try:
                pages = list(audit.pages.all() or [])
            except Exception:
                logger.exception("seo_audit.detail не удалось получить страницы audit_id=%s", audit.id)
                pages = []

            try:
                issues = list(
                    SEOIssue.objects.filter(page__audit=audit)
                    .select_related("page")
                    .order_by("page__url", "id")
                )
            except Exception:
                logger.exception("seo_audit.detail не удалось получить ошибки audit_id=%s", audit.id)
                issues = []

            try:
                audit_payload = SiteSEOAuditSerializer(audit).data
            except Exception:
                logger.exception("seo_audit.detail не удалось сериализовать аудит audit_id=%s", audit.id)
                audit_payload = {
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

            try:
                pages_payload = SEOPageSerializer(pages, many=True).data if pages else []
            except Exception:
                logger.exception("seo_audit.detail не удалось сериализовать страницы audit_id=%s", audit.id)
                pages_payload = []

            try:
                issues_payload = SEOIssueSerializer(issues, many=True).data if issues else []
            except Exception:
                logger.exception("seo_audit.detail не удалось сериализовать ошибки audit_id=%s", audit.id)
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

            response = {
                "id": audit_payload.get("id", audit.id),
                "domain": audit_payload.get("domain", audit.domain),
                "status": audit_payload.get("status", audit.status),
                "score": int(audit_payload.get("score", audit.seo_score or 0) or 0),
                "seo_score": int(audit_payload.get("seo_score", audit.seo_score or 0) or 0),
                "pages_count": int(audit_payload.get("pages_count", 0) or 0),
                "used_sitemap": bool(audit_payload.get("used_sitemap", getattr(audit, "used_sitemap", False))),
                "sitemap_urls_count": int(
                    audit_payload.get("sitemap_urls_count", getattr(audit, "sitemap_urls_count", 0)) or 0
                ),
                "pages_with_speed_issues": int(
                    audit_payload.get("pages_with_speed_issues", getattr(audit, "pages_with_speed_issues", 0)) or 0
                ),
                "pages_with_indexing_issues": int(
                    audit_payload.get(
                        "pages_with_indexing_issues",
                        getattr(audit, "pages_with_indexing_issues", 0),
                    )
                    or 0
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
            }
            if not (audit.status == SiteSEOAudit.Status.RUNNING and audit.finished_at is None):
                response["finished_at"] = audit_payload.get("finished_at", audit.finished_at)

            logger.info(
                "seo_audit.detail audit_id=%s client_id=%s status=%s score=%s pages=%s issues=%s",
                audit.id,
                request.client.id,
                audit.status,
                audit.seo_score,
                len(pages),
                len(issues),
            )
            return json_response(response, http_status=status.HTTP_200_OK)
        except Exception:
            logger.exception("seo_audit.detail ошибка audit_id=%s client_id=%s", audit_id, getattr(request.client, "id", None))
            return json_response({"detail": "Внутренняя ошибка сервера.", "ok": False}, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                        "seo_audit.stop не удалось отправить revoke audit_id=%s task_id=%s",
                        audit.id,
                        audit.celery_task_id,
                    )

            logger.info(
                "seo_audit.stop audit_id=%s client_id=%s status=%s task_id=%s",
                audit.id,
                request.client.id,
                audit.status,
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
            logger.exception("seo_audit.stop ошибка audit_id=%s client_id=%s", audit_id, getattr(request.client, "id", None))
            return json_response({"detail": "Внутренняя ошибка сервера.", "ok": False}, http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
