from telebot import types
from loader import HotelsForYou_Bot


def search_filters_markup(callback):
    mark_up = types.InlineKeyboardMarkup()
    low_price_button = types.InlineKeyboardButton(text='Low Price⤴', callback_data='PRICE,low_price')
    high_price_button = types.InlineKeyboardButton(text='High Price⤵', callback_data='PRICE_HIGHEST_FIRST,high_price')
    best_deal_button = types.InlineKeyboardButton(text='Best Deal🔄', callback_data='DISTANCE_FROM_LANDMARK,best_deal')
    mark_up.add(low_price_button, high_price_button, best_deal_button)
    HotelsForYou_Bot.send_message(callback.message.chat.id, 'Отлично, мы уже на полпути!\n'
                                                            'Теперь выберите фильтр для поиска⬇', reply_markup=mark_up)


def display_history_markup():
    mark_up = types.InlineKeyboardMarkup()
    history = types.InlineKeyboardButton(text='Search History⏮', callback_data='history')
    mark_up.add(history)
    return mark_up
