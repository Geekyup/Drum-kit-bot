from aiogram.filters.callback_data import CallbackData


class DraftAction(CallbackData, prefix="d"):
    action: str
    post_id: int
