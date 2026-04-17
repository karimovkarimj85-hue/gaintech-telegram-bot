import logging
from datetime import datetime
from html import escape

from config import NOTIFY_CHANNEL_ID

logger = logging.getLogger(__name__)


def _safe(v) -> str:
    return escape(str(v or "-"))


async def send_order_notification(bot, user_data: dict):
    """
    Отправляет в NOTIFY_CHANNEL_ID сообщение формата:

    #заказ
    ━━━━━━━━━━━━━━━━━━
    👤 Имя: {name}
    📞 Телефон: {phone}
    🆔 Telegram: @{username} (id: {user_id})
    📋 Ответы на вопросы:
      1. {answer_1}
      2. {answer_2}
      3. {answer_3}
    🕐 Время: {datetime}
    ━━━━━━━━━━━━━━━━━━
    """
    if not (NOTIFY_CHANNEL_ID or "").strip():
        logger.error("NOTIFY_CHANNEL_ID is empty. Order notification skipped.")
        return

    name = _safe(user_data.get("name"))
    phone = _safe(user_data.get("phone"))
    username = _safe(user_data.get("username"))
    user_id = _safe(user_data.get("user_id"))
    answer_1 = _safe(user_data.get("answer_1"))
    answer_2 = _safe(user_data.get("answer_2"))
    answer_3 = _safe(user_data.get("answer_3"))
    dt = datetime.now().strftime("%d.%m.%Y %H:%M")

    text = (
        "#заказ\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"🆔 Telegram: @{username} (id: {user_id})\n"
        "📋 Ответы на вопросы:\n"
        f"  1. {answer_1}\n"
        f"  2. {answer_2}\n"
        f"  3. {answer_3}\n"
        f"🕐 Время: {dt}\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    try:
        logger.info(
            f"[NOTIFY] Попытка отправки. NOTIFY_CHANNEL_ID='{NOTIFY_CHANNEL_ID}', type=order"
        )
        await bot.send_message(NOTIFY_CHANNEL_ID, text, parse_mode="HTML")
        logger.info(f"[NOTIFY] Успешно отправлено в {NOTIFY_CHANNEL_ID}")
    except Exception as e:
        logger.exception(f"[NOTIFY] ОШИБКА отправки: {e}")


async def send_consultation_notification(bot, user_data: dict):
    """
    Отправляет в NOTIFY_CHANNEL_ID сообщение формата:

    #консультация
    ━━━━━━━━━━━━━━━━━━
    👤 Имя: {name}
    📞 Телефон: {phone}
    🆔 Telegram: @{username} (id: {user_id})
    💬 Вопрос клиента: {question}
    🕐 Время: {datetime}
    ━━━━━━━━━━━━━━━━━━
    """
    if not (NOTIFY_CHANNEL_ID or "").strip():
        logger.error("NOTIFY_CHANNEL_ID is empty. Consultation notification skipped.")
        return

    name = _safe(user_data.get("name"))
    phone = _safe(user_data.get("phone"))
    username = _safe(user_data.get("username"))
    user_id = _safe(user_data.get("user_id"))
    question = _safe(user_data.get("question"))
    dt = datetime.now().strftime("%d.%m.%Y %H:%M")

    text = (
        "#консультация\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"🆔 Telegram: @{username} (id: {user_id})\n"
        f"💬 Вопрос клиента: {question}\n"
        f"🕐 Время: {dt}\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    try:
        logger.info(
            f"[NOTIFY] Попытка отправки. NOTIFY_CHANNEL_ID='{NOTIFY_CHANNEL_ID}', type=consultation"
        )
        await bot.send_message(NOTIFY_CHANNEL_ID, text, parse_mode="HTML")
        logger.info(f"[NOTIFY] Успешно отправлено в {NOTIFY_CHANNEL_ID}")
    except Exception as e:
        logger.exception(f"[NOTIFY] ОШИБКА отправки: {e}")
