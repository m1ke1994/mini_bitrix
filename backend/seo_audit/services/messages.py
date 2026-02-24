# -*- coding: utf-8 -*-
from __future__ import annotations

ISSUE_MESSAGES = {
    "missing_title": {
        "title": "Отсутствует заголовок Title.",
        "recommendation": "Добавьте уникальный Title длиной 50–60 символов с ключевыми словами страницы.",
    },
    "bad_title_length": {
        "title": "Некорректная длина заголовка Title.",
        "recommendation": "Скорректируйте длину Title до рекомендуемого диапазона 50–60 символов.",
    },
    "title_too_short": {
        "title": "Слишком короткий Title.",
        "recommendation": "Увеличьте длину Title минимум до 15 символов и конкретизируйте тему страницы.",
    },
    "title_too_long": {
        "title": "Слишком длинный Title.",
        "recommendation": "Сократите Title до 65 символов, чтобы он не обрезался в поисковой выдаче.",
    },
    "missing_description": {
        "title": "Отсутствует мета-описание (Description).",
        "recommendation": "Добавьте уникальное Description длиной 120–160 символов с кратким описанием страницы.",
    },
    "description_too_short": {
        "title": "Слишком короткое Description.",
        "recommendation": "Расширьте Description минимум до 50 символов и опишите пользу страницы для пользователя.",
    },
    "description_too_long": {
        "title": "Слишком длинное Description.",
        "recommendation": "Сократите Description до 160 символов, чтобы избежать обрезки в сниппете.",
    },
    "duplicate_title": {
        "title": "Обнаружен дублирующийся Title.",
        "recommendation": "Сделайте Title уникальным для каждой страницы с учётом её содержания и поискового запроса.",
    },
    "missing_h1": {
        "title": "Отсутствует заголовок H1.",
        "recommendation": "Добавьте один основной заголовок H1, отражающий тему страницы.",
    },
    "multiple_h1": {
        "title": "На странице используется более одного H1.",
        "recommendation": "На странице должен быть только один H1. Используйте H2–H6 для структуры.",
    },
    "long_h1": {
        "title": "Слишком длинный заголовок H1.",
        "recommendation": "Сократите H1 до 70 символов, чтобы заголовок был понятным и читаемым.",
    },
    "heading_hierarchy_gap": {
        "title": "Нарушена иерархия заголовков.",
        "recommendation": "Используйте последовательную структуру заголовков без пропусков уровней (H1 → H2 → H3).",
    },
    "low_word_count": {
        "title": "Недостаточно текстового контента на странице.",
        "recommendation": "Добавьте больше полезного текстового контента (рекомендуется минимум 300 слов).",
    },
    "image_missing_alt": {
        "title": "У изображений отсутствует атрибут alt.",
        "recommendation": "Добавьте alt-описания для информативных изображений.",
    },
    "image_empty_alt": {
        "title": "У изображений пустой атрибут alt.",
        "recommendation": "Заполните alt, если изображение несёт смысловую нагрузку; декоративные изображения можно оставить пустыми.",
    },
    "bad_status": {
        "title": "Некорректный код ответа страницы.",
        "recommendation": "Проверьте URL и серверную обработку. Страница должна возвращать код ответа 200.",
    },
    "network_error": {
        "title": "Не удалось получить страницу по сети.",
        "recommendation": "Проверьте доступность сайта, DNS, SSL-сертификат и сетевые ограничения.",
    },
    "redirect": {
        "title": "Обнаружен редирект страницы.",
        "recommendation": "Ссылайтесь сразу на конечный URL, чтобы уменьшить количество редиректов при обходе.",
    },
    "slow_response": {
        "title": "Слишком медленный ответ сервера.",
        "recommendation": "Оптимизируйте скорость ответа сервера, кеширование и отдачу контента (целевое время — до 2 секунд).",
    },
    "large_page_size": {
        "title": "Размер страницы слишком большой.",
        "recommendation": "Уменьшите размер HTML и ресурсов страницы, включите сжатие и оптимизацию статических файлов.",
    },
    "missing_canonical": {
        "title": "Отсутствует canonical-ссылка.",
        "recommendation": "Добавьте тег canonical с каноническим URL страницы.",
    },
    "missing_meta_robots": {
        "title": "Отсутствует мета-тег robots.",
        "recommendation": "Добавьте meta robots, если требуется явно управлять индексацией и переходом по ссылкам.",
    },
    "missing_viewport": {
        "title": "Отсутствует meta viewport.",
        "recommendation": "Добавьте meta viewport для корректного отображения на мобильных устройствах.",
    },
    "missing_charset": {
        "title": "Отсутствует указание кодировки страницы.",
        "recommendation": "Добавьте <meta charset=\"utf-8\"> в секцию <head> страницы.",
    },
    "missing_robots_txt": {
        "title": "Отсутствует файл robots.txt.",
        "recommendation": "Создайте robots.txt в корне сайта и укажите в нём путь к sitemap.xml.",
    },
    "robots_disallow_all": {
        "title": "robots.txt запрещает обход всего сайта.",
        "recommendation": "Удалите или скорректируйте правило Disallow: / для User-agent: *, если сайт должен индексироваться.",
    },
    "robots_missing_sitemap": {
        "title": "В robots.txt не указан sitemap.",
        "recommendation": "Добавьте директиву Sitemap с адресом файла sitemap.xml.",
    },
    "missing_sitemap": {
        "title": "Отсутствует файл sitemap.xml.",
        "recommendation": "Создайте sitemap.xml и добавьте в него основные URL сайта.",
    },
    "bad_sitemap_status": {
        "title": "Некорректный код ответа sitemap.xml.",
        "recommendation": "Проверьте доступность файла sitemap.xml. Он должен возвращать код ответа 200.",
    },
    "sitemap_mismatch": {
        "title": "Содержимое sitemap.xml не совпадает с найденными страницами.",
        "recommendation": "Актуализируйте sitemap.xml и добавьте в него реальные индексируемые страницы сайта.",
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
