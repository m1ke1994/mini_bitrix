# CONNECT

Integration reference for external websites.

## 1) Tracker Script (`tracker.js`)

```html
<script
  src="https://tracknode.ru/tracker.js"
  data-api-key="YOUR_API_KEY"
></script>
```

What tracker does:

- captures UTM/referrer/source
- sends visit/pageview/click/form/time-on-page events
- tracks scroll depth and CTA interactions
- uses `sendBeacon` on unload where possible
- sends data to `/api/track/*` and `/api/public/event/`

## 2) Widget Script (`widget.js`)

```html
<script
  src="https://tracknode.ru/widget.js"
  data-key="YOUR_API_KEY"
  data-position="bottom-right"
  data-color="#3B82F6"
  data-title="Leave your request"
  data-delay-ms="15000"
  data-exit-intent="true"
></script>
```

Widget behavior:

- launcher button + popup form
- fields: name, phone, email, message
- callback action ("call me back")
- auto-collects UTM/referrer/source
- supports timer reveal and exit intent
- sends lead to `/api/public/lead/`

## 3) Public Lead API

`POST https://yourdomain.com/api/public/lead/`

Headers:

- `Content-Type: application/json`
- `X-API-KEY: YOUR_API_KEY`

Body:

```json
{
  "name": "John",
  "phone": "+79991234567",
  "email": "john@example.com",
  "message": "Need a demo",
  "source_url": "https://site.example/landing",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "spring-2026",
  "session_id": "session-abc",
  "visitor_id": "visitor-xyz",
  "variant_id": 1
}
```

## 4) Public Event API

`POST https://yourdomain.com/api/public/event/`

Headers:

- `Content-Type: application/json`
- `X-API-KEY: YOUR_API_KEY`

Body:

```json
{
  "event_type": "visit",
  "page_url": "https://site.example/landing",
  "element_id": "hero-cta",
  "visitor_id": "visitor-xyz"
}
```

## 5) Widget A/B Variant API

Pick active variant for visitor/session:

`GET https://yourdomain.com/api/public/widget/variant/?session_id=session-abc&visitor_id=visitor-xyz`

Track impression manually (optional):

`POST https://yourdomain.com/api/public/widget/impression/`

```json
{
  "variant_id": 1
}
```
