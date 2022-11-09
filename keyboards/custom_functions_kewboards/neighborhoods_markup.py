from telebot import types
from parser_function import hotel_api_parser


def neighborhoods_markup(message):
    city_neighborhoods = hotel_api_parser.destination_id_verification(message.text)
    if city_neighborhoods:
        mark_up = types.InlineKeyboardMarkup()
        for neighborhood in city_neighborhoods:
            mark_up.add(types.InlineKeyboardButton(
                text=neighborhood['neighborhood_name'],
                callback_data=neighborhood['neighborhood_id']
            ))
        return mark_up
    else:
        return None
