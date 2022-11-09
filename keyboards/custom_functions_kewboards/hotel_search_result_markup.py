from telebot import types


def hotel_result_mark_up(text=None, prev=False, next=True, row_width=None, hotel_id=None):
    search_res_mark_up = types.InlineKeyboardMarkup(row_width=row_width)
    btn = types.InlineKeyboardButton(text=text, callback_data=text)
    next_btn = types.InlineKeyboardButton(text='>', callback_data='next_hotel')
    prev_btn = types.InlineKeyboardButton(text='<', callback_data='prev_hotel')
    photos = types.InlineKeyboardButton(text='Фото', callback_data='get_photos')
    reserve = types.InlineKeyboardButton(text='Забронировать', url=f'https://www.hotels.com/ho{hotel_id}')
    exit = types.InlineKeyboardButton(text='Закончить просмотр', callback_data='exit')
    if prev and not next:
        search_res_mark_up.add(prev_btn, btn, photos, reserve)
        search_res_mark_up.add(exit)
    elif next and not prev:
        search_res_mark_up.add(btn, next_btn, photos, reserve)
        search_res_mark_up.add(exit)
    elif prev and next:
        search_res_mark_up.add(prev_btn, btn, next_btn, photos, reserve)
        search_res_mark_up.add(exit)
    return search_res_mark_up


def hotel_photos_mark_up(text=None, prev=False, next=True, row_width=None):
    photo_res_mark_up = types.InlineKeyboardMarkup(row_width=row_width)
    btn = types.InlineKeyboardButton(text=text, callback_data=text)
    next_btn = types.InlineKeyboardButton(text='>', callback_data='next_photo')
    prev_btn = types.InlineKeyboardButton(text='<', callback_data='prev_photo')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    if prev and not next:
        photo_res_mark_up.add(prev_btn, btn, back)
    elif next and not prev:
        photo_res_mark_up.add(btn, next_btn, back)
    elif prev and next:
        photo_res_mark_up.add(prev_btn, btn, next_btn, back)
    return photo_res_mark_up


def exit_mark_up():
    final_mark_up = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton(text='Да👍', callback_data='another_search')
    exit_bot = types.InlineKeyboardButton(text='Нет👎', callback_data='see_you_soon_mate')
    final_mark_up.add(back, exit_bot)
    return final_mark_up
