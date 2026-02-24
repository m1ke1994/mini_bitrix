import logging

from django.db.models import Prefetch
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
        audit = (
            SiteSEOAudit.objects.filter(id=audit_id, client=request.client)
            .prefetch_related(
                Prefetch("pages", queryset=SEOPage.objects.order_by("url", "id")),
            )
            .first()
        )
        if not audit:
            return Response({"detail": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)

        pages = list(audit.pages.all())
        issues = list(
            SEOIssue.objects.filter(page__audit=audit)
            .select_related("page")
            .order_by("page__url", "id")
        )

        audit_payload = SiteSEOAuditSerializer(audit).data
        response = {
            "id": audit_payload["id"],
            "domain": audit_payload["domain"],
            "status": audit_payload["status"],
            "score": audit_payload["score"],
            "seo_score": audit_payload["seo_score"],
            "pages_count": audit_payload["pages_count"],
            "created_at": audit_payload["created_at"],
            "finished_at": audit_payload["finished_at"],
            "pages": SEOPageSerializer(pages, many=True).data,
            "errors": SEOIssueSerializer(issues, many=True).data,
        }
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
