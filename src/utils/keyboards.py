from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from src.utils.translations import get_translation

def get_amount_keyboard(language: str = "en"):
    """Create a compact numeric keyboard for amount input"""
    keyboard = [
        [InlineKeyboardButton("1", callback_data="amount_1"), InlineKeyboardButton("2", callback_data="amount_2"), InlineKeyboardButton("3", callback_data="amount_3"), InlineKeyboardButton("⌫", callback_data="amount_backspace")],
        [InlineKeyboardButton("4", callback_data="amount_4"), InlineKeyboardButton("5", callback_data="amount_5"), InlineKeyboardButton("6", callback_data="amount_6"), InlineKeyboardButton(".", callback_data="amount_dot")],
        [InlineKeyboardButton("7", callback_data="amount_7"), InlineKeyboardButton("8", callback_data="amount_8"), InlineKeyboardButton("9", callback_data="amount_9"), InlineKeyboardButton(get_translation("back", language), callback_data="amount_back")],
        [InlineKeyboardButton("0", callback_data="amount_0"), InlineKeyboardButton(get_translation("enter", language), callback_data="amount_enter")]
    ]
    return InlineKeyboardMarkup(keyboard)
