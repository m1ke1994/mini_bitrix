import logging

from celery.result import AsyncResult
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClientUser
from seo_audit.models import SEOIssue, SEOPage, SiteSEOAudit
from seo_audit.serializers import SEOAuditStartSerializer, SEOIssueSerializer, SEOPageSerializer, SiteSEOAuditSerializer
from subscriptions.permissions import HasActiveSubscription

logger = logging.getLogger(__name__)


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
        return Response(
            {
                "ok": True,
                "audit_id": audit.id,
                "status": audit.status,
                "domain": audit.domain,
            },
            status=status.HTTP_201_CREATED,
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
                return Response({"detail": "Audit not found.", "ok": False}, status=status.HTTP_404_NOT_FOUND)

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

            try:
                audit_payload = SiteSEOAuditSerializer(audit).data
            except Exception:
                logger.exception("seo_audit.detail failed to serialize audit audit_id=%s", audit.id)
                audit_payload = {
                    "id": audit.id,
                    "domain": audit.domain,
                    "status": audit.status,
                    "score": int(audit.seo_score or 0),
                    "seo_score": int(audit.seo_score or 0),
                    "pages_count": int(audit.pages_count or 0),
                    "created_at": audit.created_at,
                    "finished_at": audit.finished_at,
                }

            response = {
                "id": audit_payload.get("id", audit.id),
                "domain": audit_payload.get("domain", audit.domain),
                "status": audit_payload.get("status", audit.status),
                "score": int(audit_payload.get("score", audit.seo_score or 0) or 0),
                "seo_score": int(audit_payload.get("seo_score", audit.seo_score or 0) or 0),
                "pages_count": int(audit_payload.get("pages_count", 0) or 0),
                "created_at": audit_payload.get("created_at", audit.created_at),
                "pages": SEOPageSerializer(pages, many=True).data if pages else [],
                "errors": SEOIssueSerializer(issues, many=True).data if issues else [],
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
            return Response(response, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("seo_audit.detail failed audit_id=%s client_id=%s", audit_id, getattr(request.client, "id", None))
            return Response({"detail": "Internal server error.", "ok": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SEOAuditStopView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientUser, HasActiveSubscription]

    def post(self, request, audit_id: int):
        try:
            audit = SiteSEOAudit.objects.filter(id=audit_id, client=request.client).first()
            if not audit:
                return Response({"detail": "Audit not found.", "ok": False}, status=status.HTTP_404_NOT_FOUND)

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
                        "seo_audit.stop revoke failed audit_id=%s task_id=%s",
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
            return Response(
                {
                    "ok": True,
                    "audit_id": audit.id,
                    "status": audit.status,
                    "finished_at": audit.finished_at,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            logger.exception("seo_audit.stop failed audit_id=%s client_id=%s", audit_id, getattr(request.client, "id", None))
            return Response({"detail": "Internal server error.", "ok": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
