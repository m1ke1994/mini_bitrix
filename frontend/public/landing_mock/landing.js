import { homepageData } from "./homepage.js";
import { siteData } from "./data.js";

const appRoutes = {
  login: "/app/login",
  register: "/app/register",
  dashboard: "/app/dashboard",
};

const home = {
  ...homepageData,
  brand: {
    ...homepageData.brand,
    logoSrc: "/landing_media/brand/logo.svg",
  },
  headerCta: {
    ...homepageData.headerCta,
    href: appRoutes.login,
    target: "",
    rel: "",
  },
  mobileActions: [
    { label: "Войти", href: appRoutes.login },
    { label: "Зарегистрироваться", href: appRoutes.register },
  ],
  hero: {
    ...homepageData.hero,
    primaryCta: {
      ...homepageData.hero?.primaryCta,
      href: appRoutes.register,
      target: "",
      rel: "",
    },
    secondaryCta: {
      ...homepageData.hero?.secondaryCta,
      href: "#how",
      target: "",
      rel: "",
    },
  },
};

const site = {
  ...siteData,
  pricing: {
    ...siteData.pricing,
    featuredLabel: "Рекомендуем",
    contactCta: {
      href: "https://t.me/M1ke994",
      target: "_blank",
      rel: "noopener",
      label: "Связаться",
    },
  },
  reviews: {
    ...siteData.reviews,
    dateLabel: "Дата",
    items: Array.isArray(siteData.reviews?.items)
      ? siteData.reviews.items.map((item) => ({
          ...item,
          company: item.company || item.projectTitle,
        }))
      : [],
  },
  faq: {
    ...siteData.faq,
    listTitle: "Частые вопросы о сервисе",
  },
};

const how = {
  title: "Как это работает",
  subtitle: "Внесите сайт в два простых шага и получите аналитику и уведомления.",
  steps: [
    {
      id: "step-1",
      number: "1",
      title: "Добавляете сайт",
      description: "Введите адрес сайта и создайте проект в TrackNode.",
      image: "/landing_media/how/step-1.png",
      alt: "Добавление сайта",
    },
    {
      id: "step-2",
      number: "2",
      title: "Устанавливаете код",
      description: "Установите линейный код отслеживания или интеграцию.",
      image: "/landing_media/how/step-2.png",
      alt: "Установка кода отслеживания",
    },
    {
      id: "step-3",
      number: "3",
      title: "Смотрите аналитику",
      description: "Отслеживайте посещения и уведомления о заявках.",
      image: "/landing_media/how/step-3.png",
      alt: "Просмотр аналитики",
    },
  ],
  modals: {
    "step-1": {
      type: "steps",
      title: "Добавляете сайт",
      steps: [
        "Откройте TrackNode и нажмите «Создать проект».",
        "Укажите домен сайта и рабочий часовой пояс.",
        "Выберите Telegram-канал для уведомлений о заявках.",
        "Проверьте параметры проекта и сохраните настройки.",
      ],
    },
    "step-2": {
      type: "steps",
      title: "Устанавливаете код",
      steps: [
        "Скопируйте трекинг-код из карточки проекта.",
        "Добавьте код перед закрывающим тегом </head> на сайте.",
        "Если используете CMS, подключите код через шаблон или модуль.",
        "Опубликуйте изменения и выполните тестовый визит.",
        "Убедитесь, что данные начали поступать в дашборд.",
      ],
    },
    "step-3": {
      type: "example",
      title: "Пример",
      image: "/landing_media/Hero/hero.gif",
      imageAlt: "Пример аналитики TrackNode",
      text:
        "TrackNode показывает ключевые метрики в одном интерфейсе: посещения, источники, события и заявки. Команда сразу видит, где растёт конверсия, а где нужны доработки.",
    },
  },
};

const footer = {
  brand: {
    logoSrc: "/landing_media/brand/logo.svg",
    name: "TrackNode",
    href: "/",
  },
  copyright: "© 2026 TrackNode. Все права защищены.",
  legalLinks: [
    { label: "Политика конфиденциальности", href: "#" },
    { label: "Условия пользования", href: "#" },
  ],
  columns: [
    {
      title: "Продукт",
      links: [
        { label: "Возможности", href: "#features" },
        { label: "Как это работает", href: "#how" },
        { label: "Тарифы", href: "#pricing" },
        { label: "Открыть приложение", href: appRoutes.dashboard },
      ],
    },
    {
      title: "Ресурсы",
      links: [
        { label: "Отзывы", href: "#reviews" },
        { label: "FAQ", href: "#faq" },
        { label: "Поддержка", href: "#footer-contacts" },
        { label: "Документация", href: "#footer-contacts" },
      ],
    },
    {
      title: "Компания",
      links: [
        { label: "Контакты", href: "#footer-contacts" },
        { label: "Партнёрам", href: "#footer-contacts" },
        { label: "Вакансии", href: "#footer-contacts" },
        { label: "О нас", href: "#footer-contacts" },
      ],
    },
  ],
  contacts: {
    title: "Контакты",
    items: [
      {
        label: "Telegram",
        value: "@M1ke994",
        href: "https://t.me/M1ke994",
      },
      {
        label: "Email",
        value: "tishechkin1994@gmail.com",
        href: "mailto:tishechkin1994@gmail.com",
      },
      {
        label: "Телефон",
        value: "+7-901-780-05-04",
        href: "tel:+79017800504",
      },
      {
        label: "Адрес",
        value: "Россия, Москва, ул. Ленинградская, 15",
        href: "",
      },
    ],
    socials: [
      { label: "Telegram", href: "https://t.me/M1ke994", icon: "telegram" },
      { label: "VK", href: "https://example.com", icon: "vk" },
      { label: "YouTube", href: "https://example.com", icon: "youtube" },
    ],
  },
};

const heroDemo = {
  title: "Dashboard preview",
  badge: "LIVE PREVIEW",
  conversion: {
    title: "Конверсия",
    period: "за последние 7 дней",
    growth: "+7.5%",
  },
  visits: {
    title: "Визиты",
    growth: "+3.2%",
  },
  leads: {
    title: "Заявки",
    growth: "+12%",
  },
};

const seo = {
  title: "TrackNode: аналитика сайта и учёт заявок с Telegram",
  description:
    "TrackNode объединяет аналитику сайта, учёт заявок и уведомления в Telegram, чтобы контролировать лиды, источники трафика и конверсию.",
  keywords:
    "аналитика сайта, отслеживание лидов, telegram уведомления, seo аудит, конверсия сайта, учёт заявок",
  ogImage: "/landing_media/Hero/hero.gif",
  twitterCard: "summary_large_image",
};

export const landingData = {
  appRoutes,
  homepage: home,
  site,
  how,
  footer,
  heroDemo,
  seo,
};
