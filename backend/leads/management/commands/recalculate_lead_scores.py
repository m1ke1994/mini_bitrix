from django.core.management.base import BaseCommand

from leads.models import Lead
from leads.services.lead_scoring import LeadScoringService


class Command(BaseCommand):
    help = "Safely recalculate lead scores for all leads or for a specific client."

    def add_arguments(self, parser):
        parser.add_argument("--client-id", type=int, dest="client_id")

    def handle(self, *args, **options):
        queryset = Lead.objects.select_related("client").all().order_by("id")
        client_id = options.get("client_id")
        if client_id:
            queryset = queryset.filter(client_id=client_id)

        total = queryset.count()
        updated = LeadScoringService.recalculate_for_queryset(queryset)
        self.stdout.write(self.style.SUCCESS(f"Recalculated scores: total={total}, updated={updated}"))

