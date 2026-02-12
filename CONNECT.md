# CONNECT

## 1) Отправка заявки

`POST https://yourdomain.com/api/public/lead/`

Headers:

- `Content-Type: application/json`
- `X-API-KEY: ВАШ_API_KEY`

Body:

```json
{
  "name": "Иван",
  "phone": "+79999999999",
  "email": "test@mail.com",
  "message": "Хочу консультацию",
  "source_url": "https://site.ru",
  "utm_source": "instagram",
  "utm_medium": "cpc",
  "utm_campaign": "spring"
}
```

Пример `fetch`:

```javascript
await fetch("https://yourdomain.com/api/public/lead/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-KEY": "ВАШ_API_KEY"
  },
  body: JSON.stringify({
    name: "Иван",
    phone: "+79999999999",
    email: "test@mail.com",
    message: "Хочу консультацию",
    source_url: "https://site.ru",
    utm_source: "instagram",
    utm_medium: "cpc",
    utm_campaign: "spring"
  })
});
```

## 2) Отправка событий аналитики

`POST https://yourdomain.com/api/public/event/`

Headers:

- `Content-Type: application/json`
- `X-API-KEY: ВАШ_API_KEY`

Body:

```json
{
  "event_type": "visit",
  "element_id": null,
  "page_url": "https://site.ru"
}
```

Пример `fetch`:

```javascript
await fetch("https://yourdomain.com/api/public/event/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-KEY": "ВАШ_API_KEY"
  },
  body: JSON.stringify({
    event_type: "visit",
    element_id: null,
    page_url: "https://site.ru"
  })
});
```

