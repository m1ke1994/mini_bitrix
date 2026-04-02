from __future__ import annotations

from django.db.models import Q


def visit_site_client_q(client, *, prefix: str = "site__") -> Q:
    return Q(**{f"{prefix}client_id": client.id}) | Q(**{f"{prefix}token": client.api_key})


def tracker_event_site_client_q(client) -> Q:
    return visit_site_client_q(client, prefix="visit__site__")
