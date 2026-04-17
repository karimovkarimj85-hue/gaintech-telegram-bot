PORTFOLIO_ITEMS: list[dict] = [
    {
        "id": "site_001",
        "type": "site",
        "title": "Корпоративный сайт для B2B",
        "description": "Лендинг + форма заявок + базовая аналитика.",
        "url": "https://example.com/site-case",
        "preview_url": "https://example.com/site-preview.jpg",
    },
    {
        "id": "bot_001",
        "type": "bot",
        "title": "Telegram-бот для лидогенерации",
        "description": "Сбор лидов, FAQ, передача заявок менеджеру.",
        "url": "https://example.com/bot-case",
        "preview_url": "https://example.com/bot-preview.jpg",
    },
    {
        "id": "other_001",
        "type": "other",
        "title": "CRM-автоматизация продаж",
        "description": "Воронка, статусы сделок и отчёты по конверсии.",
        "url": "https://example.com/crm-case",
        "preview_url": "https://example.com/crm-preview.jpg",
    },
]


def get_items_by_type(item_type: str) -> list:
    t = (item_type or "").strip().lower()
    return [item for item in PORTFOLIO_ITEMS if (item.get("type") or "").lower() == t]


def format_portfolio_item(item) -> str:
    return (
        f"<b>{item.get('title', 'Без названия')}</b>\n"
        f"{item.get('description', '-')}\n\n"
        f"🔗 <a href=\"{item.get('url', '#')}\">Смотреть кейс</a>\n"
        f"🖼 Превью: {item.get('preview_url', '-')}"
    )
