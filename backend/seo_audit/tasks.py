import logging

from celery import shared_task
from django.utils import timezone

from seo_audit.models import SiteSEOAudit
from seo_audit.services.crawler import crawl_site_audit

logger = logging.getLogger(__name__)


@shared_task(name="seo_audit.run_site_audit")
def run_site_audit_task(audit_id: int) -> None:
    audit = SiteSEOAudit.objects.filter(id=audit_id).first()
    if not audit:
        logger.warning("seo_audit.task audit not found audit_id=%s", audit_id)
        return

    audit.status = SiteSEOAudit.Status.RUNNING
    audit.finished_at = None
    audit.save(update_fields=["status", "finished_at"])

    try:
        crawl_site_audit(audit)
    except Exception:
        logger.exception("seo_audit.task failed audit_id=%s domain=%s", audit.id, audit.domain)
        audit.status = SiteSEOAudit.Status.ERROR
        audit.finished_at = timezone.now()
        audit.save(update_fields=["status", "finished_at"])
        return

    audit.status = SiteSEOAudit.Status.DONE
    audit.finished_at = timezone.now()
    audit.save(update_fields=["status", "finished_at"])
    logger.info(
        "seo_audit.task completed audit_id=%s client_id=%s domain=%s score=%s pages_count=%s",
        audit.id,
        audit.client_id,
        audit.domain,
        audit.seo_score,
        audit.pages_count,
    )

