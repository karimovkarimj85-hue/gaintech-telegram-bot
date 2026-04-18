/** Только реальные кейсы. Новые проекты — добавляйте сюда по мере готовности. */
export const typeLabel = { site: 'Сайт', bot: 'Бот', other: 'AI / Другое' };

/**
 * Файлы из `public/` — без ведущего `/`, иначе на GitHub Pages картинка уйдёт в корень домена
 * (`user.github.io/preview.jpg`) вместо папки проекта (`user.github.io/repo/preview.jpg`).
 */
function publicAsset(path) {
  const name = String(path).replace(/^\//, '');
  const base = import.meta.env.BASE_URL ?? './';
  return base === './' || base === '.' ? `./${name}` : `${base.replace(/\/?$/, '/')}${name}`;
}

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
    preview: publicAsset('/photo-aurora.jpg'),
    previewFallback: publicAsset('/preview-gaintech.svg'),
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
    preview: publicAsset('/photo-barber.png'),
    previewFallback: publicAsset('/preview-barber.svg'),
  },
];

/** Компактный блок на странице «О нас» (4 плитки — меньше прокрутки). */
export const BENTO_ITEMS = [
  { color: '#120F17', title: 'Лиды и заявки', description: 'Чат, Web App, уведомления', label: 'Воронка' },
  { color: '#120F17', title: 'Автоматизация', description: 'Боты и сценарии под задачу', label: 'Gain Tech' },
  { color: '#120F17', title: 'Сроки', description: 'Понятные этапы и дедлайны', label: 'Процесс' },
  { color: '#120F17', title: 'Связь', description: 'Ответ до 2 ч в рабочее время', label: 'Поддержка' },
];
