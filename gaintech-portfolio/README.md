# Mini App (портфолио)

Статика для Telegram Web App. В том же репозитории, что и бот.

## Приватный репозиторий и бесплатный GitHub

На **Free** плане **GitHub Pages для приватных репозиториев недоступен** (в Settings → Pages будет предложение сделать репозиторий публичным или апгрейд).

**Варианты:**

1. **Сделать репозиторий публичным** — `Settings → General → Danger Zone → Change repository visibility → Public`. После этого включите Pages как в README ниже. Код бота и портфолио — это нормальная практика для портфолио; секреты (токены) не храните в репо, только в Railway / Secrets.
2. **Оставить репо приватным** — выложить только папку `gaintech-portfolio/` на **Cloudflare Pages**, **Netlify** или **Vercel** (бесплатные тарифы, приватный GitHub подключается). Тогда в переменной `PORTFOLIO_WEBAPP_URL` укажите выданный URL (например `https://gaintech-portfolio.pages.dev/...`).

---

## GitHub Pages (если репозиторий публичный)

1. Откройте репозиторий **gaintech-telegram-bot** на GitHub.
2. **Settings → Pages**
3. В блоке **Build and deployment** выберите **Source: GitHub Actions** (не «Deploy from a branch», если раньше не работало).
4. Сделайте push в `main` или запустите workflow **Deploy portfolio to GitHub Pages** вручную (**Actions → … → Run workflow**).

После успешного деплоя мини-приложение:

`https://karimovkarimj85-hue.github.io/gaintech-telegram-bot/index.html`

Переменная окружения бота `PORTFOLIO_WEBAPP_URL` должна совпадать с этим URL (уже задана по умолчанию в `config.py`).
