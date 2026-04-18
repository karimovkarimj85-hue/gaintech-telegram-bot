/** Только реальные кейсы. Новые проекты — добавляйте сюда по мере готовности. */
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
    /** Положите в `public/preview-gaintech.png` (ваша обложка). Если файла нет — покажется SVG. */
    preview: '/preview-gaintech.png',
    previewFallback: '/preview-gaintech.svg',
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
    preview: '/preview-barber.png',
    previewFallback: '/preview-barber.svg',
  },
];

/** Компактный блок на странице «О нас» (4 плитки — меньше прокрутки). */
export const BENTO_ITEMS = [
  { color: '#120F17', title: 'Лиды и заявки', description: 'Чат, Web App, уведомления', label: 'Воронка' },
  { color: '#120F17', title: 'Автоматизация', description: 'Боты и сценарии под задачу', label: 'Gain Tech' },
  { color: '#120F17', title: 'Сроки', description: 'Понятные этапы и дедлайны', label: 'Процесс' },
  { color: '#120F17', title: 'Связь', description: 'Ответ до 2 ч в рабочее время', label: 'Поддержка' },
];
