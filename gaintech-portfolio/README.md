# Gain Tech — мини-приложение (Vite + React)

Статика собирается в `dist/`. URL после деплоя:

`https://karimovkarimj85-hue.github.io/gaintech-telegram-bot/index.html`

## Локально

```bash
cd gaintech-portfolio
npm install
npm run dev
```

## Сборка

```bash
npm run build
```

## Превью проектов

Файлы в `public/preview-gaintech.svg` и `preview-barber.svg` — заглушки. Можно заменить на свои **PNG/WebP** с теми же именами (или поправить пути в `src/projects.js`).

## GitHub Actions

Репозиторий **public**, **Settings → Pages → Source: GitHub Actions**. Workflow собирает проект и публикует `dist/`.

## Профиль в мини-приложении

Имя и телефон сохраняются в `localStorage` (ключ `gaintech_miniapp_profile_v1`), чтобы не вводить их при каждой заявке. Кнопка «Забыть сохранённые контакты» очищает данные.
