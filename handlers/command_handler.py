from loader import HotelsForYou_Bot
from keyboards.default_commands_keyboards import start_command_markup, help_command_markup
from class_Users.class_Users import Users


@HotelsForYou_Bot.message_handler(commands=['start', 'help'])
def apply_command_funcs(message):
    """
    Функция обрабатывает команды 'start', выводя приветствие, и 'help', выводя справку о функционале бота.
    Функция также выводит InlineKeyboardMarkup для перехода к следующему шагу.
    :param message: объект Message
    :return: None
    """
    if message.text == '/start':
        user = Users.get_user(message.chat.id)
        user.name = message.from_user.first_name
        start_command_markup.start_command(message)
    if message.text == '/help':
        help_command_markup.help_command(message)
