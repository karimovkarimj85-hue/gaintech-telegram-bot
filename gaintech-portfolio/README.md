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

## Превью карточек (ваши фото)

Ожидаемые файлы (положите в `public/`):

- `preview-gaintech.png` — обложка Aurora / Gain Tech  
- `preview-barber.png` — обложка Dilshod's Barber  

Пока PNG нет в репозитории, показываются SVG из `public/preview-*.svg`. Подробности: `public/PREVIEW-IMAGES.txt`.

По умолчанию открывается вкладка **«О нас»**; **«Работы»** — два реальных бота, без плейсхолдеров «скоро».

## GitHub Actions

Репозиторий **public**, **Settings → Pages → Source: GitHub Actions**. Workflow собирает проект и публикует `dist/`.

## Профиль в мини-приложении

Имя и телефон сохраняются в `localStorage` (ключ `gaintech_miniapp_profile_v1`), чтобы не вводить их при каждой заявке. Кнопка «Забыть сохранённые контакты» очищает данные.
