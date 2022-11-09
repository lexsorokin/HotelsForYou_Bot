from telebot import types


def input_parameters(callback='input_min_price', text='Ввести минимальную цену💳', extra_callback=None, extra_text=None, extra_btn=False):
    mark_up = types.InlineKeyboardMarkup(row_width=1)
    survey = types.InlineKeyboardButton(text=text, callback_data=callback)
    extra = types.InlineKeyboardButton(text=extra_text, callback_data=extra_callback)
    if extra_btn:
        mark_up.add(survey, extra)
    else:
        mark_up.add(survey)
    return mark_up
