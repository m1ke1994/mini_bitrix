# -*- coding: utf-8 -*-
from __future__ import annotations

ISSUE_MESSAGES = {
    "missing_title": {
        "title": "Отсутствует заголовок Title.",
        "recommendation": "Добавьте уникальный Title длиной 50–60 символов с ключевой темой страницы.",
    },
    "bad_title_length": {
        "title": "Некорректная длина заголовка Title.",
        "recommendation": "Скорректируйте длину Title до рекомендуемого диапазона 50–60 символов.",
    },
    "title_too_short": {
        "title": "Слишком короткий Title.",
        "recommendation": "Увеличьте длину Title минимум до 15 символов и уточните смысл страницы.",
    },
    "title_too_long": {
        "title": "Слишком длинный Title.",
        "recommendation": "Сократите Title до 65 символов, чтобы избежать обрезки в поисковой выдаче.",
    },
    "missing_description": {
        "title": "Отсутствует meta description.",
        "recommendation": "Добавьте уникальный description длиной 120–160 символов.",
    },
    "description_too_short": {
        "title": "Слишком короткий description.",
        "recommendation": "Расширьте description минимум до 50 символов.",
    },
    "description_too_long": {
        "title": "Слишком длинный description.",
        "recommendation": "Сократите description до 160 символов.",
    },
    "duplicate_title": {
        "title": "Обнаружен дублирующийся Title.",
        "recommendation": "Сделайте Title уникальным для каждой страницы.",
    },
    "missing_h1": {
        "title": "Отсутствует заголовок H1.",
        "recommendation": "Добавьте один основной H1, отражающий тему страницы.",
    },
    "multiple_h1": {
        "title": "На странице более одного H1.",
        "recommendation": "Оставьте только один H1, используйте H2–H6 для подзаголовков.",
    },
    "long_h1": {
        "title": "Слишком длинный H1.",
        "recommendation": "Сократите H1 до 70 символов.",
    },
    "heading_hierarchy_gap": {
        "title": "Нарушена иерархия заголовков.",
        "recommendation": "Используйте последовательную структуру заголовков без пропусков уровней.",
    },
    "low_word_count": {
        "title": "Недостаточно текстового контента.",
        "recommendation": "Добавьте полезный текстовый контент, как правило от 300 слов.",
    },
    "image_missing_alt": {
        "title": "У изображений отсутствует атрибут alt.",
        "recommendation": "Добавьте alt-описания для информативных изображений.",
    },
    "image_empty_alt": {
        "title": "У изображений пустой alt.",
        "recommendation": "Заполните alt, если изображение несёт смысловую нагрузку.",
    },
    "bad_status": {
        "title": "Некорректный HTTP-статус страницы.",
        "recommendation": "Проверьте URL и серверную обработку. Страница должна отдавать HTTP 200.",
    },
    "network_error": {
        "title": "Сетевая ошибка при загрузке страницы.",
        "recommendation": "Проверьте доступность сайта, DNS, SSL и сетевые ограничения.",
    },
    "redirect": {
        "title": "Обнаружен редирект.",
        "recommendation": "Ссылайтесь сразу на конечный URL, чтобы уменьшить цепочки редиректов.",
    },
    "slow_response": {
        "title": "Медленный ответ сервера.",
        "recommendation": "Оптимизируйте backend-ответ и кеширование.",
    },
    "large_page_size": {
        "title": "Размер страницы слишком большой.",
        "recommendation": "Уменьшите общий размер HTML и ресурсов страницы.",
    },
    "slow_ttfb": {
        "title": "Высокий TTFB (медленный первый байт).",
        "recommendation": "Оптимизируйте серверный ответ, кеширование и обращения к БД.",
    },
    "large_html_size": {
        "title": "Слишком большой HTML-документ.",
        "recommendation": "Сократите объём HTML, удалите лишнюю разметку и дублирующийся контент.",
    },
    "too_many_js": {
        "title": "Слишком много JS-файлов.",
        "recommendation": "Сократите количество скриптов и используйте отложенную загрузку.",
    },
    "too_many_css": {
        "title": "Слишком много CSS-файлов.",
        "recommendation": "Объедините и оптимизируйте CSS, удалите неиспользуемые стили.",
    },
    "too_many_images": {
        "title": "Слишком много изображений.",
        "recommendation": "Сократите число изображений и включите lazy-loading.",
    },
    "heavy_js_payload": {
        "title": "Слишком тяжёлый JavaScript.",
        "recommendation": "Уменьшите размер JS-бандлов, включите code-splitting.",
    },
    "heavy_css_payload": {
        "title": "Слишком тяжёлый CSS.",
        "recommendation": "Минифицируйте и оптимизируйте CSS.",
    },
    "heavy_images_payload": {
        "title": "Слишком тяжёлые изображения.",
        "recommendation": "Сжимайте изображения, используйте WebP/AVIF и lazy-loading.",
    },
    "heavy_page_payload": {
        "title": "Слишком большой суммарный вес ресурсов.",
        "recommendation": "Оптимизируйте HTML, JS, CSS и изображения для снижения общего веса страницы.",
    },
    "missing_canonical": {
        "title": "Отсутствует canonical.",
        "recommendation": "Добавьте canonical с корректным каноническим URL страницы.",
    },
    "invalid_canonical": {
        "title": "Некорректный canonical URL.",
        "recommendation": "Укажите валидный абсолютный canonical URL с корректной схемой и доменом.",
    },
    "canonical_conflict": {
        "title": "Конфликт canonical и robots/noindex.",
        "recommendation": "Согласуйте canonical и meta robots, чтобы убрать неоднозначность индексации.",
    },
    "page_noindex": {
        "title": "Страница помечена noindex.",
        "recommendation": "Уберите noindex, если страница должна индексироваться.",
    },
    "page_nofollow": {
        "title": "Страница помечена nofollow.",
        "recommendation": "Пересмотрите nofollow, если требуется передача веса по ссылкам.",
    },
    "blocked_by_robots": {
        "title": "Страница блокируется robots.txt.",
        "recommendation": "Скорректируйте правила Disallow/Allow в robots.txt.",
    },
    "sitemap_page_missing": {
        "title": "Страница отсутствует в sitemap.xml.",
        "recommendation": "Добавьте страницу в sitemap.xml, если она должна индексироваться.",
    },
    "missing_meta_robots": {
        "title": "Отсутствует meta robots.",
        "recommendation": "Добавьте meta robots, если нужна явная политика индексации.",
    },
    "missing_viewport": {
        "title": "Отсутствует meta viewport.",
        "recommendation": "Добавьте meta viewport для корректного отображения на мобильных устройствах.",
    },
    "missing_charset": {
        "title": "Отсутствует meta charset.",
        "recommendation": "Добавьте <meta charset=\"utf-8\"> в <head>.",
    },
    "missing_robots_txt": {
        "title": "Отсутствует robots.txt.",
        "recommendation": "Создайте robots.txt в корне сайта и добавьте ссылку на sitemap.xml.",
    },
    "robots_disallow_all": {
        "title": "robots.txt запрещает обход всего сайта.",
        "recommendation": "Проверьте правило Disallow: / для User-agent: *.",
    },
    "robots_missing_sitemap": {
        "title": "В robots.txt не указан sitemap.",
        "recommendation": "Добавьте директиву Sitemap с адресом sitemap.xml.",
    },
    "missing_sitemap": {
        "title": "Отсутствует sitemap.xml.",
        "recommendation": "Создайте sitemap.xml и добавьте в него важные URL.",
    },
    "bad_sitemap_status": {
        "title": "sitemap.xml возвращает некорректный статус.",
        "recommendation": "Проверьте доступность sitemap.xml, ожидается HTTP 200.",
    },
    "sitemap_mismatch": {
        "title": "sitemap.xml не покрывает обнаруженные страницы.",
        "recommendation": "Обновите sitemap.xml и добавьте индексируемые URL.",
    },
}


def get_issue_message(issue_type: str) -> dict[str, str]:
    key = str(issue_type or "").strip()
    data = ISSUE_MESSAGES.get(key)
    if data:
        return data
    return {
        "title": f"Проблема SEO: {key or 'неизвестный тип'}.",
        "recommendation": "Проверьте страницу и устраните обнаруженную SEO-проблему.",
    }


def get_issue_title(issue_type: str) -> str:
    return get_issue_message(issue_type).get("title", "")


def get_issue_recommendation(issue_type: str) -> str:
    return get_issue_message(issue_type).get("recommendation", "")


ISSUE_GROUP_PRESETS = {
    "robots": {
        "label": "Проблемы с robots.txt",
        "description": "Поисковым системам сложнее корректно обходить сайт.",
        "target_block": "Индексация",
        "default_priority": "urgent",
    },
    "sitemap": {
        "label": "Проблемы с sitemap.xml",
        "description": "Часть страниц может индексироваться хуже, чем должна.",
        "target_block": "Индексация",
        "default_priority": "urgent",
    },
    "titles": {
        "label": "Проблемы с title и description",
        "description": "Страницы хуже выглядят в поисковой выдаче и получают меньше переходов.",
        "target_block": "Страницы",
        "default_priority": "important",
    },
    "headings": {
        "label": "Проблемы со структурой заголовков",
        "description": "Поисковику и пользователю сложнее понимать содержание страницы.",
        "target_block": "Страницы",
        "default_priority": "important",
    },
    "speed": {
        "label": "Проблемы скорости и веса страниц",
        "description": "Медленная загрузка ухудшает поведение пользователей и конверсию.",
        "target_block": "Скорость и производительность",
        "default_priority": "important",
    },
    "indexability": {
        "label": "Проблемы индексации страниц",
        "description": "Страницы могут индексироваться некорректно.",
        "target_block": "Индексация",
        "default_priority": "important",
    },
    "commercial": {
        "label": "Проблемы коммерческой готовности",
        "description": "Страницы слабо подготовлены к заявкам и обращениям.",
        "target_block": "Коммерческий SEO-аудит страницы",
        "default_priority": "important",
    },
    "status": {
        "label": "Страницы с ошибками ответа",
        "description": "Некоторые страницы недоступны или возвращают ошибки.",
        "target_block": "Ошибки",
        "default_priority": "urgent",
    },
    "other": {
        "label": "Другие SEO-замечания",
        "description": "Есть дополнительные точки улучшения сайта.",
        "target_block": "Ошибки",
        "default_priority": "later",
    },
}

ISSUE_TYPE_TO_GROUP = {
    "missing_robots_txt": "robots",
    "robots_disallow_all": "robots",
    "robots_missing_sitemap": "robots",
    "missing_sitemap": "sitemap",
    "bad_sitemap_status": "sitemap",
    "sitemap_mismatch": "sitemap",
    "sitemap_page_missing": "sitemap",
    "missing_title": "titles",
    "bad_title_length": "titles",
    "title_too_short": "titles",
    "title_too_long": "titles",
    "missing_description": "titles",
    "description_too_short": "titles",
    "description_too_long": "titles",
    "duplicate_title": "titles",
    "missing_h1": "headings",
    "multiple_h1": "headings",
    "long_h1": "headings",
    "heading_hierarchy_gap": "headings",
    "slow_response": "speed",
    "large_page_size": "speed",
    "slow_ttfb": "speed",
    "large_html_size": "speed",
    "too_many_js": "speed",
    "too_many_css": "speed",
    "too_many_images": "speed",
    "heavy_js_payload": "speed",
    "heavy_css_payload": "speed",
    "heavy_images_payload": "speed",
    "heavy_page_payload": "speed",
    "missing_canonical": "indexability",
    "invalid_canonical": "indexability",
    "canonical_conflict": "indexability",
    "page_noindex": "indexability",
    "page_nofollow": "indexability",
    "blocked_by_robots": "indexability",
    "missing_meta_robots": "indexability",
    "bad_status": "status",
    "network_error": "status",
    "redirect": "status",
}

PRIORITY_LABELS = {
    "urgent": "Срочно",
    "important": "Важно",
    "later": "Потом",
}

COMMERCIAL_STATUS_LABELS = {
    "good": "Готова к заявкам",
    "warning": "Можно усилить конверсию",
    "critical": "Слабо подготовлена",
}

COMMERCIAL_BUSINESS_STATUS_LABELS = {
    "ready": "Готова к заявкам",
    "has_channel": "Есть канал обращения",
    "improvable": "Можно усилить конверсию",
    "weak": "Слабо подготовлена",
    "none": "Нет сценария обращения",
}

CONVERSION_PATH_LABELS = {
    "form": "Классическая форма",
    "contacts": "Прямые контакты",
    "messenger": "Мессенджеры или соцсети",
    "widget": "Чат или плавающая кнопка",
    "mixed": "Смешанный сценарий",
    "none": "Не найден",
}


def get_issue_group_meta(issue_type: str) -> dict[str, str]:
    normalized = str(issue_type or "").strip().lower()
    group_key = ISSUE_TYPE_TO_GROUP.get(normalized, "other")
    preset = ISSUE_GROUP_PRESETS.get(group_key, ISSUE_GROUP_PRESETS["other"])
    return {
        "group_key": group_key,
        "label": preset["label"],
        "description": preset["description"],
        "target_block": preset["target_block"],
        "default_priority": preset["default_priority"],
    }


def get_priority_label(priority_key: str) -> str:
    return PRIORITY_LABELS.get(str(priority_key or "").strip().lower(), PRIORITY_LABELS["later"])


def _signal_bool(signals: dict | None, key: str) -> bool:
    return bool((signals or {}).get(key))


def get_commercial_business_status(
    *,
    status_key: str,
    signals: dict | None = None,
    has_conversion_path: bool | None = None,
    conversion_path_type: str | None = None,
    score: int | None = None,
) -> str:
    normalized_status = str(status_key or "").strip().lower() or "warning"
    normalized_path = str(conversion_path_type or "").strip().lower() or "none"
    has_path = bool(has_conversion_path)
    if has_conversion_path is None:
        has_path = bool(
            _signal_bool(signals, "has_conversion_path")
            or _signal_bool(signals, "has_form")
            or _signal_bool(signals, "has_direct_contact")
            or _signal_bool(signals, "has_phone_or_contact")
            or _signal_bool(signals, "has_messenger")
            or _signal_bool(signals, "has_messenger_contact")
            or _signal_bool(signals, "has_widget")
            or normalized_path in {"form", "contacts", "messenger", "widget", "mixed"}
        )

    numeric_score = int(score or 0)
    if not has_path or normalized_path == "none":
        return "none"
    if normalized_status == "good" and numeric_score >= 70:
        return "ready"
    if normalized_path in {"contacts", "messenger", "widget"} and numeric_score >= 45:
        return "has_channel"
    if normalized_status == "critical" or numeric_score < 45:
        return "weak"
    return "improvable"


def get_commercial_status_label(
    status_key: str,
    *,
    signals: dict | None = None,
    has_conversion_path: bool | None = None,
    conversion_path_type: str | None = None,
    score: int | None = None,
) -> str:
    business_key = get_commercial_business_status(
        status_key=status_key,
        signals=signals,
        has_conversion_path=has_conversion_path,
        conversion_path_type=conversion_path_type,
        score=score,
    )
    if business_key in COMMERCIAL_BUSINESS_STATUS_LABELS:
        return COMMERCIAL_BUSINESS_STATUS_LABELS[business_key]
    normalized = str(status_key or "").strip().lower()
    return COMMERCIAL_STATUS_LABELS.get(normalized, COMMERCIAL_STATUS_LABELS["warning"])


def get_conversion_path_label(path_type: str) -> str:
    key = str(path_type or "").strip().lower()
    return CONVERSION_PATH_LABELS.get(key, CONVERSION_PATH_LABELS["none"])


def get_commercial_explanation(
    *,
    signals: dict | None = None,
    has_conversion_path: bool | None = None,
    conversion_path_type: str | None = None,
    status_key: str = "warning",
    score: int | None = None,
) -> str:
    normalized_path = str(conversion_path_type or "").strip().lower() or "none"
    has_path = bool(has_conversion_path)
    if has_conversion_path is None:
        has_path = bool(
            _signal_bool(signals, "has_conversion_path")
            or normalized_path in {"form", "contacts", "messenger", "widget", "mixed"}
        )

    if not has_path or normalized_path == "none":
        return "На странице не найден явный сценарий обращения: нет формы, контактного блока, мессенджера или виджета."
    if normalized_path == "mixed":
        return "На странице есть несколько способов обращения: форма, CTA и дополнительные каналы связи."
    if normalized_path == "form":
        return "На странице есть форма заявки. Добавьте быстрый альтернативный канал связи для части пользователей."
    if normalized_path == "contacts":
        return "На странице есть прямые контакты для обращения, но классическая форма может дополнительно повысить отклик."
    if normalized_path == "messenger":
        return "На странице найден сценарий связи через мессенджеры или соцсети."
    if normalized_path == "widget":
        return "На странице найден виджет или плавающая кнопка для быстрого обращения."

    label = get_commercial_status_label(
        status_key,
        signals=signals,
        has_conversion_path=has_path,
        conversion_path_type=normalized_path,
        score=score,
    )
    return f"Текущий статус: {label}."


def get_commercial_recommendations(
    signals: dict[str, bool] | None,
    *,
    has_conversion_path: bool | None = None,
    conversion_path_type: str | None = None,
    score: int | None = None,
) -> list[str]:
    signal_map = signals or {}
    has_form = bool(signal_map.get("has_form"))
    has_cta = bool(signal_map.get("has_cta"))
    has_direct_contact = bool(signal_map.get("has_direct_contact") or signal_map.get("has_phone_or_contact"))
    has_messenger = bool(signal_map.get("has_messenger_contact") or signal_map.get("has_messenger"))
    has_widget = bool(signal_map.get("has_widget"))
    has_offer = bool(signal_map.get("has_offer_like_heading"))
    has_benefits = bool(signal_map.get("has_benefits_block"))
    has_faq = bool(signal_map.get("has_faq"))

    normalized_path = str(conversion_path_type or signal_map.get("conversion_path_type") or "").strip().lower() or "none"
    resolved_has_path = bool(has_conversion_path)
    if has_conversion_path is None:
        resolved_has_path = bool(
            signal_map.get("has_conversion_path")
            or has_form
            or has_direct_contact
            or has_messenger
            or has_widget
            or normalized_path in {"form", "contacts", "messenger", "widget", "mixed"}
        )

    rows: list[str] = []
    if not resolved_has_path or normalized_path == "none":
        rows.extend(
            [
                "Добавьте хотя бы один явный сценарий обращения: форму, мессенджер, контактный блок или чат-виджет.",
                "Сделайте заметную CTA-кнопку с прямым действием на первом экране.",
                "Добавьте контакты для быстрого обращения: телефон, email или мессенджер.",
            ]
        )
    else:
        if normalized_path in {"contacts", "messenger", "widget"} and not has_form:
            rows.append("Каналы связи уже найдены. Можно усилить конверсию короткой формой заявки.")
        if has_form and not (has_messenger or has_widget or has_direct_contact):
            rows.append("Форма найдена. Добавьте быстрый альтернативный канал связи через мессенджер или контакты.")
        if not has_cta:
            rows.append("Сценарий обращения есть. Добавьте более заметную CTA-кнопку с прямым действием.")

    if not has_offer:
        rows.append("Уточните оффер в первом экране: что получает клиент и почему это выгодно.")
    if not has_benefits:
        rows.append("Добавьте короткий блок преимуществ, чтобы повысить доверие к предложению.")
    if not has_faq:
        rows.append("Добавьте блок FAQ или ответы на типовые вопросы для снятия возражений.")

    deduplicated: list[str] = []
    for item in rows:
        if item not in deduplicated:
            deduplicated.append(item)
    return deduplicated[:5]