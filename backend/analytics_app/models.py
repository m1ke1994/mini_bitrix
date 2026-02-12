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


class PageView(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="page_views", verbose_name="Клиент")
    session_id = models.CharField(max_length=64, db_index=True, verbose_name="Session ID")
    url = models.URLField(max_length=1000, verbose_name="URL страницы")
    pathname = models.CharField(max_length=512, db_index=True, verbose_name="Pathname")
    query_string = models.TextField(blank=True, null=True, verbose_name="Query string")
    referrer = models.URLField(max_length=1000, blank=True, null=True, verbose_name="Referrer")
    utm_source = models.CharField(max_length=255, blank=True, null=True, verbose_name="UTM Source")
    utm_medium = models.CharField(max_length=255, blank=True, null=True, verbose_name="UTM Medium")
    utm_campaign = models.CharField(max_length=255, blank=True, null=True, verbose_name="UTM Campaign")
    utm_term = models.CharField(max_length=255, blank=True, null=True, verbose_name="UTM Term")
    utm_content = models.CharField(max_length=255, blank=True, null=True, verbose_name="UTM Content")
    max_scroll_depth = models.PositiveSmallIntegerField(default=0, verbose_name="Макс. глубина скролла")
    duration_seconds = models.PositiveIntegerField(default=0, verbose_name="Время на странице (сек.)")
    attributed_leads = models.PositiveIntegerField(default=0, verbose_name="Атрибутированные лиды")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Просмотр страницы"
        verbose_name_plural = "Просмотры страниц"
        indexes = [
            models.Index(fields=["client", "session_id", "created_at"]),
            models.Index(fields=["client", "pathname", "created_at"]),
        ]


class ClickEvent(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="click_events", verbose_name="Клиент")
    session_id = models.CharField(max_length=64, db_index=True, verbose_name="Session ID")
    page_pathname = models.CharField(max_length=512, db_index=True, verbose_name="Страница")
    element_text = models.CharField(max_length=100, blank=True, default="", verbose_name="Текст элемента")
    element_id = models.CharField(max_length=255, blank=True, default="", verbose_name="ID элемента")
    element_class = models.CharField(max_length=255, blank=True, default="", verbose_name="Класс элемента")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Клик"
        verbose_name_plural = "Клики"
        indexes = [
            models.Index(fields=["client", "created_at"]),
            models.Index(fields=["client", "page_pathname", "created_at"]),
        ]
