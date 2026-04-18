/** Реальные кейсы; сайты/CRM — заглушки «скоро». */
export const typeLabel = { site: 'Сайт', bot: 'Бот', other: 'AI / Другое' };

export const PROJECTS = [
  {
    id: 1,
    type: 'bot',
    featured: true,
    title: 'Aurora — Gain Tech',
    desc:
      'AI-ассистент для автоматизации продаж и заявок в Telegram: воронка лидов, мини-приложение, уведомления в канал.',
    tech: ['aiogram 3', 'Python', 'OpenRouter'],
    year: '2025',
    url: 'https://t.me/gaintech_bot',
    preview: '/preview-gaintech.svg',
  },
  {
    id: 2,
    type: 'bot',
    title: "Dilshod's Barber",
    desc:
      'Бот для барбершопа: запись к мастеру, напоминания и быстрая связь. Разработка Gain Tech.',
    tech: ['aiogram', 'Python'],
    year: '2025',
    url: 'https://t.me/dishod_barber_bot',
    preview: '/preview-barber.svg',
  },
  {
    id: 3,
    type: 'site',
    title: 'Корпоративные сайты',
    desc: 'Лендинги и многостраничные сайты под бренд. Скоро — кейсы в портфолио.',
    tech: ['Next.js', 'Tailwind'],
    year: '2025',
    url: '#',
    preview: null,
  },
  {
    id: 4,
    type: 'other',
    title: 'CRM и автоматизация',
    desc: 'Учёт заявок, задачи, интеграции. Скоро — примеры внедрений.',
    tech: ['FastAPI', 'PostgreSQL'],
    year: '2025',
    url: '#',
    preview: null,
  },
];

export const BENTO_ITEMS = [
  { color: '#120F17', title: 'Лиды', description: 'Заявки из чата и Web App', label: 'Воронка' },
  { color: '#120F17', title: 'Автоматизация', description: 'Сценарии под ваш бизнес', label: 'Gain Tech' },
  { color: '#120F17', title: 'Поддержка', description: 'Ответы 24/7 в Telegram', label: 'AI' },
  { color: '#120F17', title: 'Интеграции', description: 'CRM, таблицы, уведомления', label: 'Связки' },
  { color: '#120F17', title: 'Скорость', description: 'От прототипа до запуска', label: 'Delivery' },
  { color: '#120F17', title: 'Прозрачность', description: 'Фиксированные этапы и сроки', label: 'Процесс' },
];
