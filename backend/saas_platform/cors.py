from corsheaders.signals import check_request_enabled


def cors_allow_public_api(sender, request, **kwargs):
    return request.path.startswith("/api/public/") or request.path == "/api/analytics/event/"


check_request_enabled.connect(cors_allow_public_api)
