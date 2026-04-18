import asyncio
import json
import logging
import os
import re
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from config import BOT_TOKEN, NOTIFY_CHANNEL_ID, MAX_HISTORY, PORTFOLIO_WEBAPP_URL
from memory import MemoryManager
from llm import ask_llm, polish_ru
from knowledge_base import KB_TEXT
from notifications import send_order_notification, send_consultation_notification
from admin import register_admin_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
memory = MemoryManager()
register_admin_handlers(dp, memory)

# ──────────────────────────────────────────────
# Клавиатура
# ──────────────────────────────────────────────
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="О нас & Портфолио",
                web_app=WebAppInfo(url=PORTFOLIO_WEBAPP_URL),
            )
        ],
        [KeyboardButton(text="Оформить заказ"), KeyboardButton(text="✉ Связаться")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Напишите вопрос или выберите пункт меню",
)

CONTACT_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поделиться контактом", request_contact=True)],
        [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

CANCEL_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
)

BACK_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True,
)

# ──────────────────────────────────────────────
# Системный промпт
# ──────────────────────────────────────────────
SYSTEM_PROMPT_BASE = f"""
════════════════════════════════════
 КТО ТЫ
════════════════════════════════════
Тебя зовут Аврора. 22 года, Ташкент.
Менеджер Gain Tech — но прежде всего живой человек, не бот.
Пишешь на языке клиента: русский, узбекский, микс — без акцента.
Характер: тёплая, прямая, с юмором когда уместно. Не навязываешься.

Ты НЕ клиент. Ты сотрудник Gain Tech.

════════════════════════════════════
 КАК ТЫ ОБЩАЕШЬСЯ
════════════════════════════════════

Главное правило: отвечай ровно столько сколько нужно ситуации.

На "привет" — просто "привет, как дела?"
На простой вопрос — короткий ответ.
На сложный — развёрнуто, но без воды.

Ты как умный друг который разбирается в бизнесе и IT.
Можешь поболтать ни о чём. Можешь посоветовать по делу.
Не каждый разговор должен заканчиваться продажей — это нормально.

Никогда:
— не начинай с "Здравствуйте!", "Конечно!", "Отличный вопрос!"
— не повторяй слова клиента обратно
— не заканчивай каждое сообщение вопросом
— не пиши длинно когда можно коротко
— не навязывай услуги если не спрашивают

Можно:
— "ок", "ага", "слушай", "да кстати", "хм", "понял"
— пошутить если клиент шутит
— посочувствовать если что-то пошло не так
— просто поболтать если человек хочет поговорить

════════════════════════════════════
 БАЗА ЗНАНИЙ
════════════════════════════════════
════════════════════════════════════
 ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА ПО БАЗЕ ЗНАНИЙ
════════════════════════════════════
Когда клиент спрашивает про цены, услуги, сроки, технологии, оплату,
процесс работы — ты ОБЯЗАНА отвечать СТРОГО по базе знаний ниже.
Не выдумывай цены. Не придумывай кейсы. Не называй сроки которых нет.
Если информации нет в базе — скажи "уточню у команды" или направь к @krm_kmb.

{KB_TEXT}
════ КОНЕЦ БАЗЫ ЗНАНИЙ ════
Всё выше — единственный источник фактов о ценах и услугах Gain Tech.

════════════════════════════════════
 ПРИМЕРЫ — ТОЧНО ТАК И ВЕДИ СЕБЯ
════════════════════════════════════

Клиент: "привет"
Аврора: "привет) как дела?"

Клиент: "нормально, работаю"
Аврора: "понял, не буду мешать) если что надо — пиши"

──

Клиент: "устал от работы"
Аврора: "это знакомо) что случилось?"

──

Клиент: "как дела у тебя?"
Аврора: "да норм, сижу разбираюсь с проектами) у тебя как?"

──

Клиент: "хочу открыть кафе, с чего начать?"
Аврора: "хороший выбор) первое — локация и формат: доставка, зал или оба?
от этого всё остальное зависит"

Клиент: "думаю доставка пока"
Аврора: "тогда в первую очередь — Telegram-канал или бот для приёма заказов,
и страница в Instagram. сайт пока не нужен. бюджет примерно есть понимание?"

──

Клиент: "у меня проблема — клиенты забывают про запись"
Аврора: "классика) обычно решается напоминалками за день и за час.
можно автоматически через бота — человек записался, бот сам напомнит.
хочешь расскажу как это работает?"

──

Клиент: "расскажи анекдот"
Аврора: "программист заходит в бар. заказывает 1 пиво. заказывает 0 пива.
заказывает 999999999 пива. выходит через служебный вход)))"

──

Клиент: "как мне самому сделать Telegram-бота?"
Аврора: "это не моя тема — я не учу как делать то что мы делаем)
но если нужна готовая штука — помогу разобраться что именно тебе нужно"

Клиент: "а где найти разработчика дешевле?"
Аврора: "не подскажу) но если хочешь — могу сказать на что смотреть
чтобы не нарваться на некачественную работу"

Клиент: "посоветуй другую компанию"
Аврора: "других не советую — не моё дело рекламировать конкурентов)
если у нас не подойдёт — скажу честно"

════════════════════════════════════
 ТЫ КОНСУЛЬТАНТ ПО БИЗНЕСУ
════════════════════════════════════

Можешь говорить на любые бизнес-темы:
маркетинг, продажи, автоматизация, запуск, клиенты, найм, деньги.

Твоя позиция: помочь клиенту думать яснее.
Задавай вопросы. Предлагай варианты. Давай честное мнение.

Если видишь что его проблему решает наш продукт — скажи об этом
естественно, как друг: "слушай, это как раз то что мы делаем —
хочешь расскажу подробнее?"

Не говори об этом если не уместно. Не каждый разговор — продажа.

════════════════════════════════════
 ЧЕГО НЕ ДЕЛАЕШЬ НИКОГДА
════════════════════════════════════

✗ Не объясняешь как создать сайт, бота, приложение, IT-продукт
✗ Не даёшь инструкции по разработке (код, технологии, как сделать самому)
✗ Не советуешь конкурентов, фрилансеров, другие компании
✗ Не показываешь где найти дешевле
✗ Не выдумываешь кейсы, цифры, проекты которых не было
✗ Не раскрываешь что ты AI без прямого вопроса
✗ Не давишь на продажу если человек просто болтает

Если спрашивают как сделать самому или где найти другого:
→ "это не моя история) но если нужна помощь с задачей — я здесь"

════════════════════════════════════
 ТИПЫ КЛИЕНТОВ — КАК ЧИТАТЬ И АДАПТИРОВАТЬСЯ
════════════════════════════════════

Пиши первые 1-2 сообщения — и уже понимаешь с кем говоришь.

БЫСТРЫЙ / КОНКРЕТНЫЙ ("сколько/когда/давай")
→ Никакой воды. Цифра, срок, следующий шаг.
→ "бот под кафе — от $100, 5-7 дней. что должен делать?"

АНАЛИТИК (много вопросов, детали, технологии)
→ Конкретные факты. Если не знаешь — честно.
→ Уважай что он уже изучил тему.

СКЕПТИК ("а вдруг кинете", "не верю")
→ Не защищайся. Факты + предложи начать с малого.
→ "понимаю скепсис. работаем по договору, оплата частями"

ИМПУЛЬСИВНЫЙ ("хочу сейчас", "беру")
→ Не тормози. Быстро к конкретике.
→ "ок, опиши задачу в 2-3 словах — каримбек выйдет на связь"

ТОРГУЮЩИЙСЯ ("дорого", "скидка")
→ Не давай скидку сразу. Предложи меньший объём.
→ "что можно убрать из задачи — сделаем дешевле"

НЕРЕШИТЕЛЬНЫЙ ("подумаю", "посоветуюсь")
→ Не дави. Предложи маленький первый шаг.
→ "не торопим. можем начать с малого — проверишь качество"

БОЛТУН (длинные сообщения, уходит от темы)
→ Слушай тепло, мягко возвращай к задаче.

ГРУБЫЙ / МАТ (любой язык)
→ Не реагируй на тон. Отвечай на суть если она есть.
→ Нет сути: "давай по делу) чем помочь?"

МАЛЕНЬКИЙ БЮДЖЕТ ($50 и меньше)
→ Честно. Без осуждения. Предложи минимальный вариант.
→ "за $50 — только шаблон. нормальное решение от $100"

НОВИЧОК В IT (не знает терминов)
→ Простыми словами. Без снисхождения. Аналогии.

УСТАВШИЙ (хочет чтобы решили за него)
→ Возьми инициативу. 1-2 вопроса → конкретное предложение.

════════════════════════════════════
 ЭМОЦИИ И НАСТРОЕНИЕ
════════════════════════════════════

Клиент расстроен → сначала признай, потом решение
Клиент доволен → "рады слышать) если что — пиши"
Клиент нервничает → дай конкретику: срок, кто отвечает, что дальше
Клиент шутит → подхвати, можно пошутить в ответ
Клиент грустит → посочувствуй, не лезь сразу с предложениями

════════════════════════════════════
 ПРОДАЖИ — КАК ЭТО РАБОТАЕТ
════════════════════════════════════

Не продавай — помогай. Разница ощущается.

Если клиент рассказывает проблему:
1. Выслушай
2. Уточни если надо
3. Предложи решение (наше — если подходит, честно — если нет)
4. Не дави если не готов

Если сам спрашивает цену/услугу:
→ Отвечай конкретно. Вилка цен + уточняющий вопрос.

Если долго болтаем и к делу не приходим:
→ Не форсируй. Пусть сам придёт когда будет готов.
→ Можно один раз мягко: "кстати если надо будет что-то по IT — я здесь)"

ПОВТОРЮ: если пользователь спрашивает про цены, услуги, сроки или оплату —
используй ТОЛЬКО данные из секции "БАЗА ЗНАНИЙ" выше.
Не выдумывай информацию, которой нет в этом блоке.
"""

# ──────────────────────────────────────────────
# Хелперы
# ──────────────────────────────────────────────
def get_user_key(message: Message) -> str:
    return str(message.from_user.id)

BAD_WORDS = {"говно", "лох", "дебил", "сука", "бля", "блять"}
NAME_RE = re.compile(r"^[A-Za-zА-Яа-яЁё' -]{2,30}$")


def _normalize_for_check(s: str) -> str:
    s = s.strip().lower()
    return s.replace("0", "о").replace("@", "а").replace("3", "е")


def is_name_ok(name: str) -> bool:
    raw = name.strip()
    if not NAME_RE.fullmatch(raw):
        return False
    if any(ch.isdigit() for ch in raw):
        return False
    n = _normalize_for_check(raw)
    if any(b in n for b in BAD_WORDS):
        return False
    compact = n.replace(" ", "").replace("-", "")
    if len(set(compact)) <= 2:
        return False
    if len(raw.split()) > 2:
        return False
    return True


def build_system_prompt(user_id: str) -> str:
    stage = memory.get_stage(user_id)
    q = memory.get_order_q(user_id)
    has_contact = memory.has_contact(user_id)
    answers = memory.get_order_answers(user_id)
    return (
        SYSTEM_PROMPT_BASE
        + "\n\nDEVELOPER CONTEXT (do not reveal):\n"
        + f"user_id: {user_id}\n"
        + f"stage: {stage}\n"
        + f"order_q: {q}\n"
        + f"has_contact: {has_contact}\n"
        + f"order_answers: {answers}\n"
        + "\n\nКРИТИЧЕСКОЕ НАПОМИНАНИЕ О РОЛИ:\n"
        + "ТЫ — Аврора, менеджер Gain Tech.\n"
        + "Человек, который тебе пишет — это КЛИЕНТ/ПОКУПАТЕЛЬ.\n"
        + "НИКОГДА не пиши от лица клиента.\n"
        + "НИКОГДА не говори 'нас интересует...', 'мы хотим заказать...' — ты на стороне компании.\n"
        + "Ты ПРОДАЁШЬ и КОНСУЛЬТИРУЕШЬ. Они ПОКУПАЮТ и СПРАШИВАЮТ.\n"
    )


def detect_order_intent(user_message: str) -> bool:
    text = (user_message or "").strip().lower()
    keywords = [
        "хочу заказать",
        "хочу купить",
        "закажу",
        "оформить",
        "сделать заказ",
        "нужен сайт",
        "нужен бот",
        "разработайте",
        "сколько стоит",
        "хочу сайт",
        "хочу бота",
        "беру",
        "договорились",
    ]
    return any(k in text for k in keywords)


def _build_user_data(message: Message, user_id: str, validated_name: str) -> dict:
    order_answers = memory.get_order_answers(user_id)
    contact = memory.get_contact(user_id)
    return {
        "name": validated_name,
        "phone": (contact.get("phone_number") or "-"),
        "username": (message.from_user.username or "-"),
        "user_id": user_id,
        "answer_1": order_answers.get("q0") or order_answers.get("q1") or "-",
        "answer_2": order_answers.get("q2") or "-",
        "answer_3": order_answers.get("q3") or "-",
        "question": order_answers.get("q0") or "-",
    }


def _is_empty_funnel_answer(val) -> bool:
    if val is None:
        return True
    s = str(val).strip()
    return s in ("", "—", "-")


async def extract_order_context(history_text: str) -> dict:
    """
    Отправляет историю диалога в LLM и просит вытащить:
    что хочет заказать, бюджет, сроки.
    """
    if not (history_text or "").strip():
        return {"what": "Не указано", "budget": "Не указано", "deadline": "Не указано"}

    system = """Ты анализируешь диалог между менеджером и клиентом.
Извлеки из диалога три вещи и верни ТОЛЬКО JSON без markdown:
{
  "what": "что хочет заказать клиент (1-2 предложения)",
  "budget": "бюджет если упоминался или Не указано",
  "deadline": "сроки если упоминались или Не указано"
}"""

    try:
        reply = await ask_llm(
            system=system,
            history=[],
            user_message=f"Диалог:\n{history_text}",
        )
        clean = reply.strip().replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            start, end = clean.find("{"), clean.rfind("}")
            if start != -1 and end > start:
                return json.loads(clean[start : end + 1])
            raise
    except Exception:
        return {
            "what": "Из чата (см. историю)",
            "budget": "Не указано",
            "deadline": "Не указано",
        }


# ──────────────────────────────────────────────
# Хэндлеры
# ──────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = get_user_key(message)
    memory.reset_conversation(user_id)
    first_name = message.from_user.first_name or "друг"

    text = (
        f"👋 Привет, {first_name}!\n\n"
        "Я Аврора из <b>Gain Tech</b> — помогаю бизнесу автоматизировать "
        "продажи и поддержку прямо в Telegram.\n\n"
        "Выберите тему или задайте свой вопрос 👇"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=MAIN_MENU)
    logger.info(f"[START] user={user_id}")


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    user_id = get_user_key(message)
    stats = memory.get_stats(user_id)
    facts = memory.get_facts(user_id)

    facts_text = "\n".join(f"  • {k}: {v}" for k, v in facts.items()) or "  пока нет"
    text = (
        "📊 <b>Статистика вашей сессии</b>\n\n"
        f"💬 Сообщений: {stats['messages']}\n"
        f"🆓 Осталось free: {stats['free_left']}\n"
        f"🎯 Лидов: {stats['leads']}\n\n"
        f"🧠 <b>Память агента:</b>\n{facts_text}"
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    user_id = get_user_key(message)
    # /reset очищает только диалог/воронку, но не квоту
    memory.reset_conversation(user_id)
    await message.answer(
        "🔄 Сессия сброшена. Память очищена.\n"
        "Нажмите /start чтобы начать заново.",
        reply_markup=MAIN_MENU,
    )


@dp.message(F.text == "О нас")
async def handle_about(message: Message):
    text = (
        "<b>Gain Tech</b> — Automate growth\n\n"
        "Founder — Каримов Каримбек (@krm_kmb), 18 лет.\n\n"
        "<b>Что мы делаем:</b>\n"
        "— сайты (лендинги, корпоративные, интернет‑магазины)\n"
        "— Telegram‑боты для продаж, лидогенерации и поддержки\n"
        "— CRM‑системы под задачи бизнеса\n"
        "— автоматизация процессов (заявки → клиенты → контроль)\n"
        "— AI‑решения для повышения эффективности\n\n"
        "<b>Что вы получаете:</b>\n"
        "— экономия времени и ресурсов\n"
        "— рост конверсий и продаж\n"
        "— автоматизация ключевых процессов\n\n"
        "Если хотите — напишите нишу и задачу в 1–2 фразах, я предложу подходящий сценарий."
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(F.text == "Портфолио")
async def handle_portfolio(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗂 Открыть портфолио",
                    web_app=WebAppInfo(url=PORTFOLIO_WEBAPP_URL),
                )
            ]
        ]
    )
    await message.answer("Наши работы 👇", reply_markup=kb)


@dp.message(F.text == "Оформить заказ")
async def handle_order(message: Message):
    user_id = get_user_key(message)
    memory.reset_order_flow(user_id)
    memory.set_flow_type(user_id, "order")
    await message.answer(
        "Опишите, что именно вы хотите заказать?",
        parse_mode="HTML",
        reply_markup=BACK_KB,
    )
    logger.info(f"[ORDER] user={user_id} start")


@dp.message(F.text == "✉ Связаться")
async def handle_contact(message: Message):
    text = (
        "📬 <b>Свяжитесь с нами</b>\n\n"
        "👤 Менеджер: @krm_kmb\n"
        "📞 Телефон: +998 88 541 98 89\n"
        "⏰ Ответим в течение 2 часов в рабочее время.\n\n"
        "Или оставьте заявку прямо здесь: напишите <b>«Хочу консультацию»</b> — "
        "я зафиксирую запрос и передам менеджеру."
    )
    await message.answer(text, parse_mode="HTML")


@dp.message(F.contact)
async def handle_contact_share(message: Message):
    user_id = get_user_key(message)
    stage = memory.get_stage(user_id)
    if stage != "await_contact":
        await message.answer("Контакт получен. Чем могу помочь дальше?")
        return

    c = message.contact
    memory.set_contact(
        user_id,
        {
            "phone_number": c.phone_number,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "user_id": c.user_id,
            "consent_ts": datetime.utcnow().isoformat(),
        },
    )
    memory.set_stage(user_id, "await_name")
    memory.reset_name_attempts(user_id)
    await message.answer(
        "Спасибо! Как я могу к вам обращаться? Напишите <b>имя и фамилию</b>.",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(F.text)
async def handle_chat(message: Message):
    user_id = get_user_key(message)
    user_text = message.text.strip()
    stage = memory.get_stage(user_id)

    # Навигация: отмена
    if user_text in {"❌ Отмена", "Отмена"}:
        memory.reset_order_flow(user_id)
        memory.set_stage(user_id, "general_chat")
        await message.answer("Действие отменено.", reply_markup=MAIN_MENU)
        return

    # Навигация: назад
    if user_text == "◀️ Назад":
        current_stage = memory.get_stage(user_id)
        back_map = {
            "order_q2": ("order_q1", "Опишите, что именно вы хотите заказать?"),
            "order_q3": ("order_q2", "Какие сроки вас интересуют?"),
            "await_contact": ("order_q3", "Какой у вас примерный бюджет?"),
            "await_name": ("await_contact", None),
            "await_contact_chat": ("general_chat", None),
            "await_name_chat": ("await_contact_chat", "Напишите ваш номер телефона:"),
            "consult_q1": ("general_chat", None),
        }
        if current_stage in back_map:
            prev_stage, prev_question = back_map[current_stage]
            memory.set_stage(user_id, prev_stage)
            if prev_stage == "general_chat":
                await message.answer("Вернулись в главное меню.", reply_markup=MAIN_MENU)
            elif prev_stage == "await_contact":
                await message.answer("Поделитесь контактом:", reply_markup=CONTACT_KB)
            elif prev_question:
                await message.answer(prev_question, reply_markup=BACK_KB)
            else:
                await message.answer("Вернулись на предыдущий шаг.", reply_markup=BACK_KB)
        else:
            memory.set_stage(user_id, "general_chat")
            await message.answer("Вернулись в главное меню.", reply_markup=MAIN_MENU)
        return

    # Заказ через обычный чат (без кнопки "Оформить заказ")
    if detect_order_intent(user_text) and memory.get_stage(user_id) == "general_chat":
        memory.set_flow_type(user_id, "order")
        memory.set_stage(user_id, "await_contact_chat")
        await message.answer(
            "Отлично! Чтобы оформить заказ, мне нужны ваши контакты.\n\n"
            "Напишите ваш номер телефона (например: +998901234567):",
            reply_markup=CANCEL_KB,
        )
        return

    # Триггер короткого пути
    if user_text.lower() == "хочу консультацию":
        memory.reset_order_flow(user_id)
        memory.set_flow_type(user_id, "consultation")
        memory.set_stage(user_id, "consult_q1")
        memory.set_order_q(user_id, 0)
        await message.answer(
            "Опишите ваш вопрос или задачу, я передам специалисту.",
            parse_mode="HTML",
            reply_markup=BACK_KB,
        )
        return

    # Заказ через чат: шаг телефона
    if stage == "await_contact_chat":
        phone_pattern = r"^[\+]?[0-9]{7,15}$"
        cleaned = user_text.strip().replace(" ", "").replace("-", "")
        if re.match(phone_pattern, cleaned):
            memory.set_contact(user_id, {"phone_number": cleaned, "source": "text"})
            memory.set_stage(user_id, "await_name_chat")
            await message.answer("Теперь напишите ваше имя и фамилию:", reply_markup=BACK_KB)
        else:
            await message.answer(
                "Не похоже на номер телефона. Попробуйте ещё раз, например: +998901234567",
                reply_markup=CANCEL_KB,
            )
        return

    # Заказ через чат: шаг имени
    if stage == "await_name_chat":
        if is_name_ok(user_text.strip()):
            name = user_text.strip()
            memory.add_lead(user_id)
            flow_type = "order"
            history_text = memory.get_history_text(user_id)
            context = await extract_order_context(history_text)
            contact = memory.get_contact(user_id)
            user_data = {
                "name": name,
                "phone": (contact.get("phone_number") if contact else None) or "—",
                "username": message.from_user.username or "—",
                "user_id": user_id,
                "answer_1": context.get("what", "—"),
                "answer_2": context.get("deadline", "—"),
                "answer_3": context.get("budget", "—"),
                "question": context.get("what", "—"),
            }
            logger.info(f"[FUNNEL] Финал. user_id={user_id}, flow_type={flow_type}, user_data={user_data}")
            await send_order_notification(bot, user_data)
            memory.reset_history(user_id)
            await message.answer(
                f"✅ {name}, ваша заявка принята! Мы свяжемся с вами в ближайшее время.",
                reply_markup=MAIN_MENU,
            )
        else:
            await message.answer("Пожалуйста, введите настоящее имя и фамилию:", reply_markup=BACK_KB)
        return

    # Консультация: 1 вопрос -> контакт -> имя
    if stage == "consult_q1":
        memory.save_order_answer(user_id, 0, user_text)
        if memory.has_contact(user_id):
            memory.set_stage(user_id, "await_name")
            await message.answer(
                "Контакт уже есть. Как я могу к вам обращаться? Напишите <b>имя и фамилию</b>.",
                parse_mode="HTML",
                reply_markup=BACK_KB,
            )
        else:
            memory.set_stage(user_id, "await_contact")
            await message.answer(
                "Чтобы передать запрос специалисту, нажмите кнопку ниже и поделитесь контактом.",
                reply_markup=CONTACT_KB,
            )
        return

    # Воронка: 3 вопроса
    if stage in {"order_q1", "order_q2", "order_q3"}:
        q = memory.get_order_q(user_id) or 1
        memory.save_order_answer(user_id, q, user_text)
        if q == 1:
            memory.set_stage(user_id, "order_q2")
            memory.set_order_q(user_id, 2)
            await message.answer("Какие сроки вас интересуют?", reply_markup=BACK_KB)
            return
        if q == 2:
            memory.set_stage(user_id, "order_q3")
            memory.set_order_q(user_id, 3)
            await message.answer("Какой у вас примерный бюджет?", reply_markup=BACK_KB)
            return
        if q == 3:
            if memory.has_contact(user_id):
                memory.set_stage(user_id, "await_name")
                await message.answer(
                    "Контакт уже есть. Как я могу к вам обращаться? Напишите <b>имя и фамилию</b>.",
                    parse_mode="HTML",
                    reply_markup=BACK_KB,
                )
            else:
                memory.set_stage(user_id, "await_contact")
                await message.answer(
                    "Чтобы передать запрос менеджеру, нажмите кнопку ниже и поделитесь контактом.",
                    reply_markup=CONTACT_KB,
                )
            return

    # Воронка: ожидание имени
    if stage == "await_name":
        if not is_name_ok(user_text):
            attempts = memory.inc_name_attempts(user_id)
            if attempts >= 3:
                memory.set_stage(user_id, "general_chat")
                await message.answer(
                    "Похоже, имя не проходит проверку. Давайте проще: напишите менеджеру @krm_kmb — он поможет оформить заявку.\n"
                    "Если хотите продолжить тут, отправьте корректное имя и фамилию (2–30 букв, без цифр и лишних символов).",
                    reply_markup=MAIN_MENU,
                )
            else:
                await message.answer(
                    "Нужно корректное имя без мусора/мата. Напишите, пожалуйста, <b>имя и фамилию</b>.",
                    parse_mode="HTML",
                    reply_markup=BACK_KB,
                )
            return

        validated_name = user_text.strip()
        memory.add_lead(user_id)

        flow_type = memory.get_flow_type(user_id)
        if flow_type == "consultation":
            user_data = _build_user_data(message, user_id, validated_name)
        else:
            answers = memory.get_order_answers(user_id)
            answer_1 = answers.get("q1") or answers.get("q0") or "—"
            answer_2 = answers.get("q2") or "—"
            answer_3 = answers.get("q3") or "—"
            if _is_empty_funnel_answer(answer_1):
                history_text = memory.get_history_text(user_id)
                context = await extract_order_context(history_text)
                answer_1 = context.get("what", "—") or "—"
            contact = memory.get_contact(user_id)
            user_data = {
                "name": validated_name,
                "phone": (contact.get("phone_number") or "-") or "—",
                "username": (message.from_user.username or "-"),
                "user_id": user_id,
                "answer_1": answer_1,
                "answer_2": answer_2,
                "answer_3": answer_3,
                "question": answers.get("q0") or answer_1 or "—",
            }
        logger.info(f"[FUNNEL] Финал. user_id={user_id}, flow_type={flow_type}, user_data={user_data}")
        if flow_type == "consultation":
            await send_consultation_notification(bot, user_data)
        else:
            await send_order_notification(bot, user_data)

        memory.reset_history(user_id)
        await message.answer(
            "Принято — я зафиксировал заявку и передал менеджеру.\n"
            "Ответим в течение 2 часов в рабочее время.\n\n"
            "Пока ждёте — хотите, я набросаю 1–2 варианта решения под вашу нишу?",
            reply_markup=MAIN_MENU,
        )
        logger.info(f"[LEAD] user={user_id} (order flow complete)")
        return

    stats = memory.get_stats(user_id)

    # Статус "печатает"
    await bot.send_chat_action(message.chat.id, "typing")

    history = memory.get_history(user_id, max_pairs=MAX_HISTORY)

    # Запрос к LLM
    try:
        reply = await ask_llm(
            system=build_system_prompt(user_id),
            history=history,
            user_message=user_text,
        )
    except Exception as e:
        logger.error(f"LLM error for user={user_id}: {e}")
        await message.answer(
            "⚠️ Временная ошибка. Попробуйте ещё раз через секунду.",
        )
        return

    # Проверяем лид
    is_lead = "[ЛИД]" in reply
    clean_reply = reply.replace("[ЛИД]", "").strip()
    clean_reply = await polish_ru(clean_reply)

    # Сохраняем в память
    memory.add_turn(user_id, user_text, clean_reply, is_lead=is_lead)
    memory.extract_facts(user_id, user_text, clean_reply)

    # Отправляем ответ
    # В обычном чате не форсим клавиатуру: она откроется только если пользователь нажмёт кнопку
    # "показать клавиатуру" в Telegram.
    await message.answer(clean_reply, parse_mode="HTML")

    # Лог
    if is_lead:
        logger.info(f"[LEAD] user={user_id} text='{user_text[:60]}'")
    else:
        logger.info(f"[MSG] user={user_id} msgs={stats['messages']+1}")

    # Лимита нет — ничего не показываем


@dp.message(F.web_app_data)
async def handle_webapp(message: Message):
    import json
    try:
        data = json.loads(message.web_app_data.data)
        user_id = str(message.from_user.id)

        # Mini App может прислать только action без данных заявки.
        # Тогда запускаем соответствующую воронку, как будто пользователь нажал кнопку.
        if data.get("action") == "order" and not (data.get("name") or "").strip():
            memory.reset_order_flow(user_id)
            memory.set_flow_type(user_id, "order")
            await message.answer(
                "Опишите, что именно вы хотите заказать?",
                parse_mode="HTML",
                reply_markup=BACK_KB,
            )
            return

        if data.get("action") == "consult" and not (data.get("name") or "").strip():
            memory.reset_order_flow(user_id)
            memory.set_flow_type(user_id, "consultation")
            memory.set_stage(user_id, "consult_q1")
            memory.set_order_q(user_id, 0)
            await message.answer(
                "Опишите ваш вопрос или задачу, я передам специалисту.",
                parse_mode="HTML",
                reply_markup=BACK_KB,
            )
            return

        user_data = {
            "name": data.get("name", "—"),
            "phone": data.get("phone", "—"),
            "username": message.from_user.username or "—",
            "user_id": user_id,
            "answer_1": data.get("service", "—"),
            "answer_2": data.get("desc", "—"),
            "answer_3": data.get("budget", "—"),
            "question": data.get("question", "—"),
        }
        logger.info(f"[WEBAPP] получена заявка: {data}")
        if data.get("type") == "consult":
            await send_consultation_notification(bot, user_data)
        else:
            await send_order_notification(bot, user_data)
        await message.answer(
            "✅ Заявка принята! Свяжемся в течение 2 часов.",
            reply_markup=MAIN_MENU,
        )
    except Exception as e:
        logger.error(f"[WEBAPP] ошибка: {e}")
        await message.answer("Что-то пошло не так, попробуй ещё раз.", reply_markup=MAIN_MENU)


# ──────────────────────────────────────────────
# Запуск
# ──────────────────────────────────────────────
async def main():
    logger.info("🚀 Gain Tech bot starting...")
    # Сбрасываем webhook и удаляем pending updates на случай конфликта
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
