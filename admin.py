import os

from aiogram import F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]


def is_admin(user_id) -> bool:
    try:
        return int(user_id) in ADMIN_IDS
    except Exception:
        return False


def _admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"),
                InlineKeyboardButton(text="➕ Добавить в портфолио", callback_data="admin:add_portfolio"),
            ],
            [InlineKeyboardButton(text="📋 Заявки", callback_data="admin:leads")],
        ]
    )


def register_admin_handlers(dp, memory):
    @dp.message(Command("admin"))
    async def admin_cmd(message: Message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("⛔ Доступ запрещён.")
            return
        await message.answer("Панель администратора:", reply_markup=_admin_menu_kb())

    @dp.callback_query(F.data == "admin:stats")
    async def admin_stats(callback: CallbackQuery):
        user_id = callback.from_user.id
        if not is_admin(user_id):
            await callback.answer("⛔ Нет доступа", show_alert=True)
            return
        stats = memory.get_stats(str(user_id))
        text = (
            "<b>📊 Статистика администратора</b>\n\n"
            f"💬 Сообщений: {stats['messages']}\n"
            f"🎯 Лидов: {stats['leads']}\n"
            f"🆓 Осталось free: {stats['free_left']}\n"
            f"💳 Paid: {stats['paid']}"
        )
        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()

    @dp.callback_query(F.data == "admin:add_portfolio")
    async def admin_add_portfolio(callback: CallbackQuery):
        user_id = callback.from_user.id
        if not is_admin(user_id):
            await callback.answer("⛔ Нет доступа", show_alert=True)
            return
        await callback.message.answer("В разработке")
        await callback.answer()

    @dp.callback_query(F.data == "admin:leads")
    async def admin_leads(callback: CallbackQuery):
        user_id = callback.from_user.id
        if not is_admin(user_id):
            await callback.answer("⛔ Нет доступа", show_alert=True)
            return
        await callback.message.answer("В разработке")
        await callback.answer()
