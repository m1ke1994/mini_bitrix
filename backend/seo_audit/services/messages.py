# -*- coding: utf-8 -*-
from __future__ import annotations

ISSUE_MESSAGES = {
    "missing_title": {
        "title": "Отсутствует заголовок Title.",
        "recommendation": "Добавьте уникальный Title длиной 50-60 символов с ключевой темой страницы.",
    },
    "bad_title_length": {
        "title": "Некорректная длина заголовка Title.",
        "recommendation": "Скорректируйте длину Title до рекомендуемого диапазона 50-60 символов.",
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
        "recommendation": "Добавьте уникальный description длиной 120-160 символов.",
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
        "recommendation": "Оставьте только один H1, используйте H2-H6 для подзаголовков.",
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
        "recommendation": "Добавьте полезный текстовый контент (как правило, от 300 слов).",
    },
    "image_missing_alt": {
        "title": "У изображений отсутствует атрибут alt.",
        "recommendation": "Добавьте alt-описания для информативных изображений.",
    },
    "image_empty_alt": {
        "title": "У изображений пустой alt.",
        "recommendation": "Заполните alt, если изображение несет смысловую нагрузку.",
    },
    "bad_status": {
        "title": "Некорректный HTTP-статус страницы.",
        "recommendation": "Проверьте URL и серверную обработку. Страница должна отдавать 200.",
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
        "recommendation": "Оптимизируйте backend-ответ и кэширование.",
    },
    "large_page_size": {
        "title": "Размер страницы слишком большой.",
        "recommendation": "Уменьшите общий размер HTML и ресурсов страницы.",
    },
    "slow_ttfb": {
        "title": "Высокий TTFB (медленный первый байт).",
        "recommendation": "Оптимизируйте серверный ответ, кэширование и обращения к БД.",
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
