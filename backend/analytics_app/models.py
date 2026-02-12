from django.db import models

from clients.models import Client


class Event(models.Model):
    class EventType(models.TextChoices):
        VISIT = "visit", "Визит"
        CLICK = "click", "Клик"
        FORM_SUBMIT = "form_submit", "Отправка формы"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="events", verbose_name="Клиент")
    event_type = models.CharField(max_length=20, choices=EventType.choices, verbose_name="Тип события")
    element_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID элемента")
    page_url = models.URLField(max_length=1000, verbose_name="URL страницы")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Событие"
        verbose_name_plural = "События"
        indexes = [
            models.Index(fields=["client", "event_type", "created_at"]),
        ]
