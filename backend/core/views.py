from django.http import JsonResponse


def custom_404(request, exception):
    return JsonResponse({"error": "Страница не найдена"}, status=404)
