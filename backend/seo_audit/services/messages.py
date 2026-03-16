# -*- coding: utf-8 -*-
from __future__ import annotations

ISSUE_MESSAGES = {
    "missing_title": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ Р·Р°РіРѕР»РѕРІРѕРє Title.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ СѓРЅРёРєР°Р»СЊРЅС‹Р№ Title РґР»РёРЅРѕР№ 50-60 СЃРёРјРІРѕР»РѕРІ СЃ РєР»СЋС‡РµРІРѕР№ С‚РµРјРѕР№ СЃС‚СЂР°РЅРёС†С‹.",
    },
    "bad_title_length": {
        "title": "РќРµРєРѕСЂСЂРµРєС‚РЅР°СЏ РґР»РёРЅР° Р·Р°РіРѕР»РѕРІРєР° Title.",
        "recommendation": "РЎРєРѕСЂСЂРµРєС‚РёСЂСѓР№С‚Рµ РґР»РёРЅСѓ Title РґРѕ СЂРµРєРѕРјРµРЅРґСѓРµРјРѕРіРѕ РґРёР°РїР°Р·РѕРЅР° 50-60 СЃРёРјРІРѕР»РѕРІ.",
    },
    "title_too_short": {
        "title": "РЎР»РёС€РєРѕРј РєРѕСЂРѕС‚РєРёР№ Title.",
        "recommendation": "РЈРІРµР»РёС‡СЊС‚Рµ РґР»РёРЅСѓ Title РјРёРЅРёРјСѓРј РґРѕ 15 СЃРёРјРІРѕР»РѕРІ Рё СѓС‚РѕС‡РЅРёС‚Рµ СЃРјС‹СЃР» СЃС‚СЂР°РЅРёС†С‹.",
    },
    "title_too_long": {
        "title": "РЎР»РёС€РєРѕРј РґР»РёРЅРЅС‹Р№ Title.",
        "recommendation": "РЎРѕРєСЂР°С‚РёС‚Рµ Title РґРѕ 65 СЃРёРјРІРѕР»РѕРІ, С‡С‚РѕР±С‹ РёР·Р±РµР¶Р°С‚СЊ РѕР±СЂРµР·РєРё РІ РїРѕРёСЃРєРѕРІРѕР№ РІС‹РґР°С‡Рµ.",
    },
    "missing_description": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ meta description.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ СѓРЅРёРєР°Р»СЊРЅС‹Р№ description РґР»РёРЅРѕР№ 120-160 СЃРёРјРІРѕР»РѕРІ.",
    },
    "description_too_short": {
        "title": "РЎР»РёС€РєРѕРј РєРѕСЂРѕС‚РєРёР№ description.",
        "recommendation": "Р Р°СЃС€РёСЂСЊС‚Рµ description РјРёРЅРёРјСѓРј РґРѕ 50 СЃРёРјРІРѕР»РѕРІ.",
    },
    "description_too_long": {
        "title": "РЎР»РёС€РєРѕРј РґР»РёРЅРЅС‹Р№ description.",
        "recommendation": "РЎРѕРєСЂР°С‚РёС‚Рµ description РґРѕ 160 СЃРёРјРІРѕР»РѕРІ.",
    },
    "duplicate_title": {
        "title": "РћР±РЅР°СЂСѓР¶РµРЅ РґСѓР±Р»РёСЂСѓСЋС‰РёР№СЃСЏ Title.",
        "recommendation": "РЎРґРµР»Р°Р№С‚Рµ Title СѓРЅРёРєР°Р»СЊРЅС‹Рј РґР»СЏ РєР°Р¶РґРѕР№ СЃС‚СЂР°РЅРёС†С‹.",
    },
    "missing_h1": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ Р·Р°РіРѕР»РѕРІРѕРє H1.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ РѕРґРёРЅ РѕСЃРЅРѕРІРЅРѕР№ H1, РѕС‚СЂР°Р¶Р°СЋС‰РёР№ С‚РµРјСѓ СЃС‚СЂР°РЅРёС†С‹.",
    },
    "multiple_h1": {
        "title": "РќР° СЃС‚СЂР°РЅРёС†Рµ Р±РѕР»РµРµ РѕРґРЅРѕРіРѕ H1.",
        "recommendation": "РћСЃС‚Р°РІСЊС‚Рµ С‚РѕР»СЊРєРѕ РѕРґРёРЅ H1, РёСЃРїРѕР»СЊР·СѓР№С‚Рµ H2-H6 РґР»СЏ РїРѕРґР·Р°РіРѕР»РѕРІРєРѕРІ.",
    },
    "long_h1": {
        "title": "РЎР»РёС€РєРѕРј РґР»РёРЅРЅС‹Р№ H1.",
        "recommendation": "РЎРѕРєСЂР°С‚РёС‚Рµ H1 РґРѕ 70 СЃРёРјРІРѕР»РѕРІ.",
    },
    "heading_hierarchy_gap": {
        "title": "РќР°СЂСѓС€РµРЅР° РёРµСЂР°СЂС…РёСЏ Р·Р°РіРѕР»РѕРІРєРѕРІ.",
        "recommendation": "РСЃРїРѕР»СЊР·СѓР№С‚Рµ РїРѕСЃР»РµРґРѕРІР°С‚РµР»СЊРЅСѓСЋ СЃС‚СЂСѓРєС‚СѓСЂСѓ Р·Р°РіРѕР»РѕРІРєРѕРІ Р±РµР· РїСЂРѕРїСѓСЃРєРѕРІ СѓСЂРѕРІРЅРµР№.",
    },
    "low_word_count": {
        "title": "РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ С‚РµРєСЃС‚РѕРІРѕРіРѕ РєРѕРЅС‚РµРЅС‚Р°.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ РїРѕР»РµР·РЅС‹Р№ С‚РµРєСЃС‚РѕРІС‹Р№ РєРѕРЅС‚РµРЅС‚ (РєР°Рє РїСЂР°РІРёР»Рѕ, РѕС‚ 300 СЃР»РѕРІ).",
    },
    "image_missing_alt": {
        "title": "РЈ РёР·РѕР±СЂР°Р¶РµРЅРёР№ РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ Р°С‚СЂРёР±СѓС‚ alt.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ alt-РѕРїРёСЃР°РЅРёСЏ РґР»СЏ РёРЅС„РѕСЂРјР°С‚РёРІРЅС‹С… РёР·РѕР±СЂР°Р¶РµРЅРёР№.",
    },
    "image_empty_alt": {
        "title": "РЈ РёР·РѕР±СЂР°Р¶РµРЅРёР№ РїСѓСЃС‚РѕР№ alt.",
        "recommendation": "Р—Р°РїРѕР»РЅРёС‚Рµ alt, РµСЃР»Рё РёР·РѕР±СЂР°Р¶РµРЅРёРµ РЅРµСЃРµС‚ СЃРјС‹СЃР»РѕРІСѓСЋ РЅР°РіСЂСѓР·РєСѓ.",
    },
    "bad_status": {
        "title": "РќРµРєРѕСЂСЂРµРєС‚РЅС‹Р№ HTTP-СЃС‚Р°С‚СѓСЃ СЃС‚СЂР°РЅРёС†С‹.",
        "recommendation": "РџСЂРѕРІРµСЂСЊС‚Рµ URL Рё СЃРµСЂРІРµСЂРЅСѓСЋ РѕР±СЂР°Р±РѕС‚РєСѓ. РЎС‚СЂР°РЅРёС†Р° РґРѕР»Р¶РЅР° РѕС‚РґР°РІР°С‚СЊ 200.",
    },
    "network_error": {
        "title": "РЎРµС‚РµРІР°СЏ РѕС€РёР±РєР° РїСЂРё Р·Р°РіСЂСѓР·РєРµ СЃС‚СЂР°РЅРёС†С‹.",
        "recommendation": "РџСЂРѕРІРµСЂСЊС‚Рµ РґРѕСЃС‚СѓРїРЅРѕСЃС‚СЊ СЃР°Р№С‚Р°, DNS, SSL Рё СЃРµС‚РµРІС‹Рµ РѕРіСЂР°РЅРёС‡РµРЅРёСЏ.",
    },
    "redirect": {
        "title": "РћР±РЅР°СЂСѓР¶РµРЅ СЂРµРґРёСЂРµРєС‚.",
        "recommendation": "РЎСЃС‹Р»Р°Р№С‚РµСЃСЊ СЃСЂР°Р·Сѓ РЅР° РєРѕРЅРµС‡РЅС‹Р№ URL, С‡С‚РѕР±С‹ СѓРјРµРЅСЊС€РёС‚СЊ С†РµРїРѕС‡РєРё СЂРµРґРёСЂРµРєС‚РѕРІ.",
    },
    "slow_response": {
        "title": "РњРµРґР»РµРЅРЅС‹Р№ РѕС‚РІРµС‚ СЃРµСЂРІРµСЂР°.",
        "recommendation": "РћРїС‚РёРјРёР·РёСЂСѓР№С‚Рµ backend-РѕС‚РІРµС‚ Рё РєСЌС€РёСЂРѕРІР°РЅРёРµ.",
    },
    "large_page_size": {
        "title": "Р Р°Р·РјРµСЂ СЃС‚СЂР°РЅРёС†С‹ СЃР»РёС€РєРѕРј Р±РѕР»СЊС€РѕР№.",
        "recommendation": "РЈРјРµРЅСЊС€РёС‚Рµ РѕР±С‰РёР№ СЂР°Р·РјРµСЂ HTML Рё СЂРµСЃСѓСЂСЃРѕРІ СЃС‚СЂР°РЅРёС†С‹.",
    },
    "slow_ttfb": {
        "title": "Р’С‹СЃРѕРєРёР№ TTFB (РјРµРґР»РµРЅРЅС‹Р№ РїРµСЂРІС‹Р№ Р±Р°Р№С‚).",
        "recommendation": "РћРїС‚РёРјРёР·РёСЂСѓР№С‚Рµ СЃРµСЂРІРµСЂРЅС‹Р№ РѕС‚РІРµС‚, РєСЌС€РёСЂРѕРІР°РЅРёРµ Рё РѕР±СЂР°С‰РµРЅРёСЏ Рє Р‘Р”.",
    },
    "large_html_size": {
        "title": "РЎР»РёС€РєРѕРј Р±РѕР»СЊС€РѕР№ HTML-РґРѕРєСѓРјРµРЅС‚.",
        "recommendation": "РЎРѕРєСЂР°С‚РёС‚Рµ РѕР±СЉС‘Рј HTML, СѓРґР°Р»РёС‚Рµ Р»РёС€РЅСЋСЋ СЂР°Р·РјРµС‚РєСѓ Рё РґСѓР±Р»РёСЂСѓСЋС‰РёР№СЃСЏ РєРѕРЅС‚РµРЅС‚.",
    },
    "too_many_js": {
        "title": "РЎР»РёС€РєРѕРј РјРЅРѕРіРѕ JS-С„Р°Р№Р»РѕРІ.",
        "recommendation": "РЎРѕРєСЂР°С‚РёС‚Рµ РєРѕР»РёС‡РµСЃС‚РІРѕ СЃРєСЂРёРїС‚РѕРІ Рё РёСЃРїРѕР»СЊР·СѓР№С‚Рµ РѕС‚Р»РѕР¶РµРЅРЅСѓСЋ Р·Р°РіСЂСѓР·РєСѓ.",
    },
    "too_many_css": {
        "title": "РЎР»РёС€РєРѕРј РјРЅРѕРіРѕ CSS-С„Р°Р№Р»РѕРІ.",
        "recommendation": "РћР±СЉРµРґРёРЅРёС‚Рµ Рё РѕРїС‚РёРјРёР·РёСЂСѓР№С‚Рµ CSS, СѓРґР°Р»РёС‚Рµ РЅРµРёСЃРїРѕР»СЊР·СѓРµРјС‹Рµ СЃС‚РёР»Рё.",
    },
    "too_many_images": {
        "title": "РЎР»РёС€РєРѕРј РјРЅРѕРіРѕ РёР·РѕР±СЂР°Р¶РµРЅРёР№.",
        "recommendation": "РЎРѕРєСЂР°С‚РёС‚Рµ С‡РёСЃР»Рѕ РёР·РѕР±СЂР°Р¶РµРЅРёР№ Рё РІРєР»СЋС‡РёС‚Рµ lazy-loading.",
    },
    "heavy_js_payload": {
        "title": "РЎР»РёС€РєРѕРј С‚СЏР¶С‘Р»С‹Р№ JavaScript.",
        "recommendation": "РЈРјРµРЅСЊС€РёС‚Рµ СЂР°Р·РјРµСЂ JS-Р±Р°РЅРґР»РѕРІ, РІРєР»СЋС‡РёС‚Рµ code-splitting.",
    },
    "heavy_css_payload": {
        "title": "РЎР»РёС€РєРѕРј С‚СЏР¶С‘Р»С‹Р№ CSS.",
        "recommendation": "РњРёРЅРёС„РёС†РёСЂСѓР№С‚Рµ Рё РѕРїС‚РёРјРёР·РёСЂСѓР№С‚Рµ CSS.",
    },
    "heavy_images_payload": {
        "title": "РЎР»РёС€РєРѕРј С‚СЏР¶С‘Р»С‹Рµ РёР·РѕР±СЂР°Р¶РµРЅРёСЏ.",
        "recommendation": "РЎР¶РёРјР°Р№С‚Рµ РёР·РѕР±СЂР°Р¶РµРЅРёСЏ, РёСЃРїРѕР»СЊР·СѓР№С‚Рµ WebP/AVIF Рё lazy-loading.",
    },
    "heavy_page_payload": {
        "title": "РЎР»РёС€РєРѕРј Р±РѕР»СЊС€РѕР№ СЃСѓРјРјР°СЂРЅС‹Р№ РІРµСЃ СЂРµСЃСѓСЂСЃРѕРІ.",
        "recommendation": "РћРїС‚РёРјРёР·РёСЂСѓР№С‚Рµ HTML, JS, CSS Рё РёР·РѕР±СЂР°Р¶РµРЅРёСЏ РґР»СЏ СЃРЅРёР¶РµРЅРёСЏ РѕР±С‰РµРіРѕ РІРµСЃР° СЃС‚СЂР°РЅРёС†С‹.",
    },
    "missing_canonical": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ canonical.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ canonical СЃ РєРѕСЂСЂРµРєС‚РЅС‹Рј РєР°РЅРѕРЅРёС‡РµСЃРєРёРј URL СЃС‚СЂР°РЅРёС†С‹.",
    },
    "invalid_canonical": {
        "title": "РќРµРєРѕСЂСЂРµРєС‚РЅС‹Р№ canonical URL.",
        "recommendation": "РЈРєР°Р¶РёС‚Рµ РІР°Р»РёРґРЅС‹Р№ Р°Р±СЃРѕР»СЋС‚РЅС‹Р№ canonical URL СЃ РєРѕСЂСЂРµРєС‚РЅРѕР№ СЃС…РµРјРѕР№ Рё РґРѕРјРµРЅРѕРј.",
    },
    "canonical_conflict": {
        "title": "РљРѕРЅС„Р»РёРєС‚ canonical Рё robots/noindex.",
        "recommendation": "РЎРѕРіР»Р°СЃСѓР№С‚Рµ canonical Рё meta robots, С‡С‚РѕР±С‹ СѓР±СЂР°С‚СЊ РЅРµРѕРґРЅРѕР·РЅР°С‡РЅРѕСЃС‚СЊ РёРЅРґРµРєСЃР°С†РёРё.",
    },
    "page_noindex": {
        "title": "РЎС‚СЂР°РЅРёС†Р° РїРѕРјРµС‡РµРЅР° noindex.",
        "recommendation": "РЈР±РµСЂРёС‚Рµ noindex, РµСЃР»Рё СЃС‚СЂР°РЅРёС†Р° РґРѕР»Р¶РЅР° РёРЅРґРµРєСЃРёСЂРѕРІР°С‚СЊСЃСЏ.",
    },
    "page_nofollow": {
        "title": "РЎС‚СЂР°РЅРёС†Р° РїРѕРјРµС‡РµРЅР° nofollow.",
        "recommendation": "РџРµСЂРµСЃРјРѕС‚СЂРёС‚Рµ nofollow, РµСЃР»Рё С‚СЂРµР±СѓРµС‚СЃСЏ РїРµСЂРµРґР°С‡Р° РІРµСЃР° РїРѕ СЃСЃС‹Р»РєР°Рј.",
    },
    "blocked_by_robots": {
        "title": "РЎС‚СЂР°РЅРёС†Р° Р±Р»РѕРєРёСЂСѓРµС‚СЃСЏ robots.txt.",
        "recommendation": "РЎРєРѕСЂСЂРµРєС‚РёСЂСѓР№С‚Рµ РїСЂР°РІРёР»Р° Disallow/Allow РІ robots.txt.",
    },
    "sitemap_page_missing": {
        "title": "РЎС‚СЂР°РЅРёС†Р° РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РІ sitemap.xml.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ СЃС‚СЂР°РЅРёС†Сѓ РІ sitemap.xml, РµСЃР»Рё РѕРЅР° РґРѕР»Р¶РЅР° РёРЅРґРµРєСЃРёСЂРѕРІР°С‚СЊСЃСЏ.",
    },
    "missing_meta_robots": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ meta robots.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ meta robots, РµСЃР»Рё РЅСѓР¶РЅР° СЏРІРЅР°СЏ РїРѕР»РёС‚РёРєР° РёРЅРґРµРєСЃР°С†РёРё.",
    },
    "missing_viewport": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ meta viewport.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ meta viewport РґР»СЏ РєРѕСЂСЂРµРєС‚РЅРѕРіРѕ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ РЅР° РјРѕР±РёР»СЊРЅС‹С… СѓСЃС‚СЂРѕР№СЃС‚РІР°С….",
    },
    "missing_charset": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ meta charset.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ <meta charset=\"utf-8\"> РІ <head>.",
    },
    "missing_robots_txt": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ robots.txt.",
        "recommendation": "РЎРѕР·РґР°Р№С‚Рµ robots.txt РІ РєРѕСЂРЅРµ СЃР°Р№С‚Р° Рё РґРѕР±Р°РІСЊС‚Рµ СЃСЃС‹Р»РєСѓ РЅР° sitemap.xml.",
    },
    "robots_disallow_all": {
        "title": "robots.txt Р·Р°РїСЂРµС‰Р°РµС‚ РѕР±С…РѕРґ РІСЃРµРіРѕ СЃР°Р№С‚Р°.",
        "recommendation": "РџСЂРѕРІРµСЂСЊС‚Рµ РїСЂР°РІРёР»Рѕ Disallow: / РґР»СЏ User-agent: *.",
    },
    "robots_missing_sitemap": {
        "title": "Р’ robots.txt РЅРµ СѓРєР°Р·Р°РЅ sitemap.",
        "recommendation": "Р”РѕР±Р°РІСЊС‚Рµ РґРёСЂРµРєС‚РёРІСѓ Sitemap СЃ Р°РґСЂРµСЃРѕРј sitemap.xml.",
    },
    "missing_sitemap": {
        "title": "РћС‚СЃСѓС‚СЃС‚РІСѓРµС‚ sitemap.xml.",
        "recommendation": "РЎРѕР·РґР°Р№С‚Рµ sitemap.xml Рё РґРѕР±Р°РІСЊС‚Рµ РІ РЅРµРіРѕ РІР°Р¶РЅС‹Рµ URL.",
    },
    "bad_sitemap_status": {
        "title": "sitemap.xml РІРѕР·РІСЂР°С‰Р°РµС‚ РЅРµРєРѕСЂСЂРµРєС‚РЅС‹Р№ СЃС‚Р°С‚СѓСЃ.",
        "recommendation": "РџСЂРѕРІРµСЂСЊС‚Рµ РґРѕСЃС‚СѓРїРЅРѕСЃС‚СЊ sitemap.xml, РѕР¶РёРґР°РµС‚СЃСЏ HTTP 200.",
    },
    "sitemap_mismatch": {
        "title": "sitemap.xml РЅРµ РїРѕРєСЂС‹РІР°РµС‚ РѕР±РЅР°СЂСѓР¶РµРЅРЅС‹Рµ СЃС‚СЂР°РЅРёС†С‹.",
        "recommendation": "РћР±РЅРѕРІРёС‚Рµ sitemap.xml Рё РґРѕР±Р°РІСЊС‚Рµ РёРЅРґРµРєСЃРёСЂСѓРµРјС‹Рµ URL.",
    },
}


def get_issue_message(issue_type: str) -> dict[str, str]:
    key = str(issue_type or "").strip()
    data = ISSUE_MESSAGES.get(key)
    if data:
        return data
    return {
        "title": f"РџСЂРѕР±Р»РµРјР° SEO: {key or 'РЅРµРёР·РІРµСЃС‚РЅС‹Р№ С‚РёРї'}.",
        "recommendation": "РџСЂРѕРІРµСЂСЊС‚Рµ СЃС‚СЂР°РЅРёС†Сѓ Рё СѓСЃС‚СЂР°РЅРёС‚Рµ РѕР±РЅР°СЂСѓР¶РµРЅРЅСѓСЋ SEO-РїСЂРѕР±Р»РµРјСѓ.",
    }


def get_issue_title(issue_type: str) -> str:
    return get_issue_message(issue_type).get("title", "")


def get_issue_recommendation(issue_type: str) -> str:
    return get_issue_message(issue_type).get("recommendation", "")


ISSUE_GROUP_PRESETS = {
    "robots": {
        "label": "РџСЂРѕР±Р»РµРјС‹ СЃ robots.txt",
        "description": "РџРѕРёСЃРєРѕРІС‹Рј СЃРёСЃС‚РµРјР°Рј СЃР»РѕР¶РЅРµРµ РєРѕСЂСЂРµРєС‚РЅРѕ РѕР±С…РѕРґРёС‚СЊ СЃР°Р№С‚.",
        "target_block": "РРЅРґРµРєСЃР°С†РёСЏ",
        "default_priority": "urgent",
    },
    "sitemap": {
        "label": "РџСЂРѕР±Р»РµРјС‹ СЃ sitemap.xml",
        "description": "Р§Р°СЃС‚СЊ СЃС‚СЂР°РЅРёС† РјРѕР¶РµС‚ РёРЅРґРµРєСЃРёСЂРѕРІР°С‚СЊСЃСЏ С…СѓР¶Рµ, С‡РµРј РґРѕР»Р¶РЅР°.",
        "target_block": "РРЅРґРµРєСЃР°С†РёСЏ",
        "default_priority": "urgent",
    },
    "titles": {
        "label": "РџСЂРѕР±Р»РµРјС‹ СЃ title Рё description",
        "description": "РЎС‚СЂР°РЅРёС†С‹ С…СѓР¶Рµ РІС‹РіР»СЏРґСЏС‚ РІ РІС‹РґР°С‡Рµ Рё РїРѕР»СѓС‡Р°СЋС‚ РјРµРЅСЊС€Рµ РїРµСЂРµС…РѕРґРѕРІ.",
        "target_block": "РЎС‚СЂР°РЅРёС†С‹",
        "default_priority": "important",
    },
    "headings": {
        "label": "РџСЂРѕР±Р»РµРјС‹ СЃРѕ СЃС‚СЂСѓРєС‚СѓСЂРѕР№ Р·Р°РіРѕР»РѕРІРєРѕРІ",
        "description": "РџРѕРёСЃРєРѕРІРёРєСѓ Рё РїРѕР»СЊР·РѕРІР°С‚РµР»СЋ СЃР»РѕР¶РЅРµРµ РїРѕРЅРёРјР°С‚СЊ СЃРѕРґРµСЂР¶Р°РЅРёРµ СЃС‚СЂР°РЅРёС†С‹.",
        "target_block": "РЎС‚СЂР°РЅРёС†С‹",
        "default_priority": "important",
    },
    "speed": {
        "label": "РџСЂРѕР±Р»РµРјС‹ СЃРєРѕСЂРѕСЃС‚Рё Рё РІРµСЃР° СЃС‚СЂР°РЅРёС†",
        "description": "РњРµРґР»РµРЅРЅР°СЏ Р·Р°РіСЂСѓР·РєР° СѓС…СѓРґС€Р°РµС‚ РїРѕРІРµРґРµРЅРёРµ РїРѕР»СЊР·РѕРІР°С‚РµР»РµР№ Рё РєРѕРЅРІРµСЂСЃРёСЋ.",
        "target_block": "РЎРєРѕСЂРѕСЃС‚СЊ Рё РїСЂРѕРёР·РІРѕРґРёС‚РµР»СЊРЅРѕСЃС‚СЊ",
        "default_priority": "important",
    },
    "indexability": {
        "label": "РџСЂРѕР±Р»РµРјС‹ РёРЅРґРµРєСЃР°С†РёРё СЃС‚СЂР°РЅРёС†",
        "description": "РЎС‚СЂР°РЅРёС†С‹ РјРѕРіСѓС‚ РёРЅРґРµРєСЃРёСЂРѕРІР°С‚СЊСЃСЏ РЅРµРєРѕСЂСЂРµРєС‚РЅРѕ.",
        "target_block": "РРЅРґРµРєСЃР°С†РёСЏ",
        "default_priority": "important",
    },
    "commercial": {
        "label": "РџСЂРѕР±Р»РµРјС‹ РєРѕРјРјРµСЂС‡РµСЃРєРѕР№ РіРѕС‚РѕРІРЅРѕСЃС‚Рё",
        "description": "РЎС‚СЂР°РЅРёС†С‹ СЃР»Р°Р±Рѕ РїРѕРґРіРѕС‚РѕРІР»РµРЅС‹ Рє Р·Р°СЏРІРєР°Рј Рё РѕР±СЂР°С‰РµРЅРёСЏРј.",
        "target_block": "РљРѕРјРјРµСЂС‡РµСЃРєРёР№ SEO-Р°СѓРґРёС‚ СЃС‚СЂР°РЅРёС†С‹",
        "default_priority": "important",
    },
    "status": {
        "label": "РЎС‚СЂР°РЅРёС†С‹ СЃ РѕС€РёР±РєР°РјРё РѕС‚РІРµС‚Р°",
        "description": "РќРµРєРѕС‚РѕСЂС‹Рµ СЃС‚СЂР°РЅРёС†С‹ РЅРµРґРѕСЃС‚СѓРїРЅС‹ РёР»Рё РІРѕР·РІСЂР°С‰Р°СЋС‚ РѕС€РёР±РєРё.",
        "target_block": "РћС€РёР±РєРё",
        "default_priority": "urgent",
    },
    "other": {
        "label": "Р”СЂСѓРіРёРµ SEO-Р·Р°РјРµС‡Р°РЅРёСЏ",
        "description": "Р•СЃС‚СЊ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹Рµ С‚РѕС‡РєРё СѓР»СѓС‡С€РµРЅРёСЏ СЃР°Р№С‚Р°.",
        "target_block": "РћС€РёР±РєРё",
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
    "urgent": "РЎСЂРѕС‡РЅРѕ",
    "important": "Р’Р°Р¶РЅРѕ",
    "later": "РџРѕС‚РѕРј",
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
