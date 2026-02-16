from django.http import HttpResponse


class TrackerCorsMiddleware:
    """Force permissive CORS contract for public tracker endpoints."""

    TRACK_PREFIX = "/api/track/"
    ALLOW_METHODS = "GET, POST, OPTIONS"
    ALLOW_HEADERS = "Content-Type, Authorization, X-Requested-With"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.TRACK_PREFIX) and request.method == "OPTIONS":
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)

        if request.path.startswith(self.TRACK_PREFIX):
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = self.ALLOW_METHODS
            response["Access-Control-Allow-Headers"] = self.ALLOW_HEADERS
            response["Access-Control-Max-Age"] = "86400"

        return response
