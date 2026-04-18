# Mini App (портфолио)

Статика для Telegram Web App. В том же репозитории, что и бот.

## GitHub Pages (обязательно, иначе будет 404)

1. Откройте репозиторий **gaintech-telegram-bot** на GitHub.
2. **Settings → Pages**
3. В блоке **Build and deployment** выберите **Source: GitHub Actions** (не «Deploy from a branch», если раньше не работало).
4. Сделайте push в `main` или запустите workflow **Deploy portfolio to GitHub Pages** вручную (**Actions → … → Run workflow**).

После успешного деплоя мини-приложение:

`https://karimovkarimj85-hue.github.io/gaintech-telegram-bot/index.html`

Переменная окружения бота `PORTFOLIO_WEBAPP_URL` должна совпадать с этим URL (уже задана по умолчанию в `config.py`).
