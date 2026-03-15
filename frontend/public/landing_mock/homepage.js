export const homepageData = {
  brand: { name: "TrackNode" },
  nav: [
    {
      label: "Главная",
      href: "/",
      children: [
        { label: "Возможности", href: "#capabilities" },
        { label: "Как работает", href: "#how" },
        { label: "Отзывы", href: "#reviews" },
        { label: "Тарифы", href: "#pricing" },
        { label: "FAQ", href: "#faq" },
        { label: "Контакты", href: "#contacts" },
      ],
    },
    { label: "SEO-аудит", href: "/seo-audit" },
    { label: "Аналитика сайта", href: "/website-analytics" },
    { label: "Кейсы", href: "/cases" },
    { label: "Цены", href: "/pricing" },
    { label: "Статьи", href: "/blog" },
    { label: "Контакты", href: "/contacts" },
  ],
  headerCta: { label: "Войти", href: "https://tracknode.ru", target: "_blank", rel: "noopener" },
  hero: {
    titleLines: [
      "Аналитика сайта,",
      "уведомления о заявках",
      "в Telegram и SEO-аудит —",
      "в одном сервисе",
    ],
    description:
      "TrackNode фиксирует новые заявки и лиды с сайта и мгновенно отправляет уведомления в Telegram. Дополнительно показывает аналитику посещений и источников трафика и помогает находить SEO и технические ошибки.",
    primaryCta: { label: "Зарегистрироваться", href: "https://tracknode.ru", target: "_blank", rel: "noopener" },
    secondaryCta: { label: "Подключить сайт", href: "#how" },
  },
  trust: {
    title: "Используют для контроля заявок и роста конверсии",
    items: ["Company", "Brand", "Studio", "Agency", "Startup", "Business", "Business"],
  },
};
