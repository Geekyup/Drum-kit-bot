from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callbacks import DraftAction


def draft_kb(post_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Опубликовать", callback_data=DraftAction(action="publish", post_id=post_id))
    builder.button(text="❌ Отклонить", callback_data=DraftAction(action="reject", post_id=post_id))
    builder.adjust(2)
    return builder.as_markup()
