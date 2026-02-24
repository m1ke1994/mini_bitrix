from django.urls import path

from seo_audit.views import SEOAuditDetailView, SEOAuditStartView

urlpatterns = [
    path("start/", SEOAuditStartView.as_view(), name="seo_audit_start"),
    path("<int:audit_id>/", SEOAuditDetailView.as_view(), name="seo_audit_detail"),
]
