from telebot import types
from loader import HotelsForYou_Bot


def start_command(message):
    mark_up = types.InlineKeyboardMarkup(row_width=1)
    start_button = types.InlineKeyboardButton(text='Fly me to the Moon✈', callback_data='start_search')
    mark_up.add(start_button)
    HotelsForYou_Bot.send_message(message.chat.id,
                                  f'Hola, {message.from_user.first_name}!\n'
                                  f'Вас приветствует HotelsForYou - телеграмм бот '
                                  f'для поиска отелей в любой точке мира.\n'
                                  'Для знакомства с командами бота нажмите /help.\n'
                                  '\nAND REMEMBER - THE WORLD IS YOUR OYSTER! :)', reply_markup=mark_up)
