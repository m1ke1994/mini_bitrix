from django.conf import settings
from django.db import models

from clients.models import Client


class Pipeline(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="pipelines", verbose_name="Клиент")
    name = models.CharField(max_length=120, default="Основная", verbose_name="Название")
    is_default = models.BooleanField(default=False, verbose_name="По умолчанию")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        ordering = ("client_id", "name")
        verbose_name = "Воронка"
        verbose_name_plural = "Воронки"
        constraints = [
            models.UniqueConstraint(
                fields=["client"],
                condition=models.Q(is_default=True),
                name="leads_unique_default_pipeline_per_client",
            ),
        ]

    def __str__(self):
        return f"{self.client.name}: {self.name}"


class PipelineStage(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="stages", verbose_name="Воронка")
    name = models.CharField(max_length=120, verbose_name="Название")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="Порядок")
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Цвет")
    auto_action = models.JSONField(blank=True, null=True, verbose_name="Авто-действия")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    is_closed_stage = models.BooleanField(default=False, verbose_name="Финальная стадия")

    class Meta:
        ordering = ("pipeline_id", "order", "id")
        verbose_name = "Стадия воронки"
        verbose_name_plural = "Стадии воронки"
        constraints = [
            models.UniqueConstraint(fields=["pipeline", "order"], name="leads_unique_stage_order_per_pipeline"),
        ]

    def __str__(self):
        return f"{self.pipeline.name}: {self.name}"


class Tag(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="lead_tags", verbose_name="Клиент")
    name = models.CharField(max_length=80, verbose_name="Название")
    color = models.CharField(max_length=7, default="#64748B", verbose_name="Цвет")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ("client_id", "name")
        verbose_name = "Тег лида"
        verbose_name_plural = "Теги лидов"
        constraints = [
            models.UniqueConstraint(fields=["client", "name"], name="leads_unique_tag_name_per_client"),
        ]

    def __str__(self):
        return self.name


class WidgetVariant(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="widget_variants", verbose_name="Клиент")
    name = models.CharField(max_length=120, verbose_name="Название варианта")
    config = models.JSONField(default=dict, blank=True, verbose_name="Конфигурация")
    impressions = models.PositiveIntegerField(default=0, verbose_name="Показы")
    conversions = models.PositiveIntegerField(default=0, verbose_name="Конверсии")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        ordering = ("client_id", "-is_active", "name")
        verbose_name = "Вариант виджета"
        verbose_name_plural = "Варианты виджета"
        constraints = [
            models.UniqueConstraint(fields=["client", "name"], name="leads_unique_widget_variant_name_per_client"),
        ]

    @property
    def conversion_rate(self) -> float:
        if not self.impressions:
            return 0.0
        return round((self.conversions / self.impressions) * 100.0, 2)

    def __str__(self):
        return f"{self.client.name}: {self.name}"


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        CLOSED = "closed", "Закрыта"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="leads", verbose_name="Клиент")
    name = models.CharField(max_length=255, blank=True, default="", verbose_name="Имя")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телефон")
    normalized_phone = models.CharField(max_length=32, blank=True, default="", db_index=True, verbose_name="Телефон (норм.)")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    normalized_email = models.CharField(max_length=255, blank=True, default="", db_index=True, verbose_name="Email (норм.)")
    message = models.TextField(blank=True, null=True, verbose_name="Сообщение")
    source_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name="URL страницы")
    utm_source = models.CharField(max_length=255, blank=True, null=True, verbose_name="UTM Source")
    utm_medium = models.CharField(max_length=255, blank=True, null=True, verbose_name="UTM Medium")
    utm_campaign = models.CharField(max_length=255, blank=True, null=True, verbose_name="UTM Campaign")
    session_id = models.CharField(max_length=64, blank=True, default="", db_index=True, verbose_name="Session ID")
    visitor_id = models.CharField(max_length=64, blank=True, default="", db_index=True, verbose_name="Visitor ID")
    tracker_submission_id = models.CharField(max_length=128, blank=True, default="", db_index=True, verbose_name="Tracker submission ID")
    tracker_dedup_key = models.CharField(max_length=96, blank=True, default="", db_index=True, verbose_name="Tracker dedup key")
    stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
        verbose_name="Стадия",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name="Статус")
    score = models.PositiveSmallIntegerField(default=0, verbose_name="Скоринг")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
        verbose_name="Ответственный",
    )
    next_contact_at = models.DateTimeField(null=True, blank=True, verbose_name="Следующий контакт")
    last_activity_at = models.DateTimeField(null=True, blank=True, verbose_name="Последняя активность")
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Оценочная ценность",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="leads", verbose_name="Теги")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        indexes = [
            models.Index(fields=["client", "status", "created_at"]),
            models.Index(fields=["client", "stage", "created_at"]),
            models.Index(fields=["client", "normalized_phone"]),
            models.Index(fields=["client", "normalized_email"]),
            models.Index(fields=["client", "score"]),
            models.Index(fields=["client", "last_activity_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["client", "tracker_dedup_key"],
                condition=~models.Q(tracker_dedup_key=""),
                name="leads_unique_tracker_dedup_key_per_client",
            ),
        ]

    def __str__(self):
        return f"{self.name or 'Без имени'} ({self.phone or 'без телефона'})"


class LeadActivity(models.Model):
    class ActionType(models.TextChoices):
        CREATED = "created", "Создан лид"
        STAGE_MOVED = "stage_moved", "Перемещение по стадиям"
        NOTE_ADDED = "note_added", "Добавлена заметка"
        SCHEDULED = "scheduled", "Запланирован контакт"
        DUPLICATE_MERGED = "duplicate_merged", "Объединен дубликат"
        SCORE_UPDATED = "score_updated", "Обновлен скоринг"
        AUTO_RESPONSE = "auto_response", "Автоответ"
        NOTIFIED = "notified", "Уведомление"

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="activities", verbose_name="Лид")
    action_type = models.CharField(max_length=64, choices=ActionType.choices, verbose_name="Тип действия")
    description = models.TextField(blank=True, default="", verbose_name="Описание")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_activities",
        verbose_name="Кем создано",
    )
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Метаданные")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Создано")

    class Meta:
        ordering = ("-created_at", "id")
        verbose_name = "Активность лида"
        verbose_name_plural = "Активности лидов"
        indexes = [
            models.Index(fields=["lead", "action_type", "created_at"]),
            models.Index(fields=["lead", "created_at"]),
        ]

    def __str__(self):
        return f"Lead #{self.lead_id}: {self.action_type}"
