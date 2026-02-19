from datetime import datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone

from analytics_app.models import Event
from leads.models import Lead
from tracker.models import Visit


def default_period_days(days: int = 14):
    now = timezone.localtime()
    date_to = now.date()
    date_from = date_to - timedelta(days=max(1, days) - 1)
    return date_from, date_to


def period_bounds(date_from, date_to, tz=None):
    tz = tz or timezone.get_current_timezone()
    from_dt = timezone.make_aware(datetime.combine(date_from, time.min), tz)
    to_dt = timezone.make_aware(datetime.combine(date_to, time.max), tz)
    return from_dt, to_dt


def get_metrics(client, date_from, date_to):
    from_dt, to_dt = period_bounds(date_from, date_to)

    visits_qs = Visit.objects.filter(
        site__token=client.api_key,
        started_at__gte=from_dt,
        started_at__lte=to_dt,
    )
    forms_qs = Event.objects.filter(
        client=client,
        event_type=Event.EventType.FORM_SUBMIT,
        created_at__gte=from_dt,
        created_at__lte=to_dt,
    ).exclude(element_id="fetch_json")
    leads_qs = Lead.objects.filter(
        client=client,
        created_at__gte=from_dt,
        created_at__lte=to_dt,
    )

    visits = visits_qs.count()
    forms = forms_qs.count()
    leads = leads_qs.count()

    with_id_filter = Q(visitor_id__isnull=False) & ~Q(visitor_id="")
    unique_with_visitor_id = visits_qs.filter(with_id_filter).values("visitor_id").distinct().count()
    unique_without_visitor_id = visits_qs.exclude(with_id_filter).values("session_id").distinct().count()
    unique_users = unique_with_visitor_id + unique_without_visitor_id

    # Count form submits as conversions for tracker-based funnels.
    conversion_events = max(forms, leads)
    conversion = round((conversion_events / visits) * 100, 2) if visits > 0 else 0.0

    return {
        "visits": visits,
        "unique_users": unique_users,
        "forms": forms,
        "leads": leads,
        "conversion_events": conversion_events,
        "conversion": conversion,
        "from_dt": from_dt,
        "to_dt": to_dt,
    }
