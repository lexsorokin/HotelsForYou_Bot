from telebot import types


def verify_info(correct_callback='proceed', incorrect_callback='from_the_top'):
    mark_up = types.InlineKeyboardMarkup()
    proceed_button = types.InlineKeyboardButton(text='Все верно!👍', callback_data=correct_callback)
    incorrect = types.InlineKeyboardButton(text='Я заметил ошибку...👎', callback_data=incorrect_callback)
    mark_up.add(proceed_button, incorrect)
    return mark_up



