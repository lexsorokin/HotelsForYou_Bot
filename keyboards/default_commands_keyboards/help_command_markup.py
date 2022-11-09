from telebot import types
from loader import HotelsForYou_Bot


def help_command(message):
    mark_up = types.InlineKeyboardMarkup(row_width=1)
    start_button = types.InlineKeyboardButton(text='Got It! Fly me to the Moon ✈', callback_data='start_search')
    mark_up.add(start_button)
    HotelsForYou_Bot.send_message(message.chat.id,
                                  'Low Price — вывод самых дешёвых отелей в городе\n'
                                  'High Price — вывод самых дорогих отелей в городе\n'
                                  'Best Deal — вывод отелей, наиболее подходящих по цене и расположению от центра\n'
                                  'History — вывод истории поиска', reply_markup=mark_up)