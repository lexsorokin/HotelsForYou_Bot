from loader import HotelsForYou_Bot
from parser_function import hotel_api_parser
from keyboards.custom_functions_kewboards import neighborhoods_markup, search_filters_markup, calendar_markup, \
    verify_information_markup, hotel_search_result_markup, best_deal_survey_markup
from datetime import datetime, timedelta
import time
from class_Users.class_Users import Users
from telebot.types import CallbackQuery, Message, InputMediaPhoto
from database.search_history import SearchHistory, save_result_to_db


@HotelsForYou_Bot.callback_query_handler(func=lambda callback: callback.data in ['start_search',
                                                                                 'from_the_top',
                                                                                 'another_search'])
def get_city_destination(callback: CallbackQuery) -> None:
    """
    Шаг 1.

    Функция создает объект класса User или вытаскивает уже существующего пользователя по id.

    Далее запрашивает направление у пользователя и передает полученную информацию в следующую функцию.
    :param callback: callback.data 'start_search' и 'from_the_top'
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)
    user.check_in = None
    user.check_out = None
    if callback.data == 'start_search':
        history_mark_up = search_filters_markup.display_history_markup()
        destination = HotelsForYou_Bot.send_message(callback.message.chat.id, 'Введите <b>НАПРАВЛЕНИЕ</b> или '
                                                                              'посмотрите <b>ИСТОРИЮ ПОИСКА</b>⬇',
                                                    parse_mode='HTML',
                                                    reply_markup=history_mark_up)
        HotelsForYou_Bot.register_next_step_handler(destination, show_neighborhoods)
    elif callback.data == 'from_the_top':
        user.input_history.delete_instance()
        destination = HotelsForYou_Bot.send_message(callback.message.chat.id, 'Ничего страшного! Давайте пройдемся по '
                                                                              'информации снова:\n '
                                                                              '\nВведите <b>НАПРАВЛЕНИЕ</b>⬇',
                                                    parse_mode='HTML')
        HotelsForYou_Bot.register_next_step_handler(destination, show_neighborhoods)

    elif callback.data == 'another_search':
        user.input_history = None
        try:
            get_name = SearchHistory.select().where(
                SearchHistory.user_id == callback.message.chat.id and SearchHistory.user_name != 'Null').get()
            history_mark_up = search_filters_markup.display_history_markup()
            destination = HotelsForYou_Bot.send_message(callback.message.chat.id,
                                                        f'И снова здравствуйте, {get_name.user_name}!🙂\n'
                                                        '\nВведите <b>НАПРАВЛЕНИЕ</b> или '
                                                        'посмотрите <b>ИСТОРИЮ ПОИСКА</b>⬇',
                                                        reply_markup=history_mark_up,
                                                        parse_mode='HTML', )
        except:
            history_mark_up = search_filters_markup.display_history_markup()
            destination = HotelsForYou_Bot.send_message(callback.message.chat.id,
                                                        f'И снова здравствуйте!🙂\n'
                                                        '\nВведите <b>НАПРАВЛЕНИЕ</b> или '
                                                        'посмотрите <b>ИСТОРИЮ ПОИСКА</b>⬇',
                                                        reply_markup=history_mark_up,
                                                        parse_mode='HTML')
        HotelsForYou_Bot.register_next_step_handler(destination, show_neighborhoods)


def show_neighborhoods(message: Message) -> None:
    """
    Шаг 2.

    Функция сохраняет название города.

    Далее функция создает строчку в базе данных, сохраняет ее в аттрибут класса Users и записывает в нее user_id и
    имя пользователя.

    Далее, сперва проверяя корректность ввода, функция выводит варианты возможных районов данного города и сами города с
    похожим названием с помощью Inline клавиатуры, кнопки которой содержат в себе callback с id выбранного района/города
    для сужения круга поиска.
    :param message: объект Message.
    :return: None
    """
    print(message.text)
    mark_up = neighborhoods_markup.neighborhoods_markup(message)
    if mark_up:
        HotelsForYou_Bot.send_message(message.chat.id,
                                      'Уточните <b>НАПРАВЛЕНИЕ</b>⬇',
                                      reply_markup=mark_up,
                                      parse_mode='HTML')
    else:
        destination = HotelsForYou_Bot.send_message(chat_id=message.chat.id,
                                                    text='Данное направление не найдено😔\n'
                                                         'Попробуйте ввести <b>НАПРАВЛЕНИЕ</b> снова⬇',
                                                    parse_mode='HTML')
        HotelsForYou_Bot.register_next_step_handler(destination, show_neighborhoods)


@HotelsForYou_Bot.callback_query_handler(func=lambda callback: callback.data.isdigit() and len(callback.data) > 1)
def get_search_filters(callback: CallbackQuery) -> None:
    """
    Шаг 3.

    Функция принимает id района из callback.data, сохраняя данную информацию.
    Далее функция выводит Inline клавиатуру, для выбора типа сортировки данных при поиске.
    :param callback: callback.data с id района.
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)
    user.dest_id = callback.data
    search_filters_markup.search_filters_markup(callback)


@HotelsForYou_Bot.callback_query_handler(func=lambda callback: callback.data in ['PRICE,low_price',
                                                                                 'PRICE_HIGHEST_FIRST,high_price',
                                                                                 'DISTANCE_FROM_LANDMARK,best_deal'])
def show_calendar(callback: CallbackQuery) -> None:
    """
    Шаг 4.

    Функция принимает callback.data, сохраняя тип сортировки.
    Далее функция создает динамический календарь для выбора даты заезда.
    :param callback: callback.data с типом сортировки
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)
    user.sort_order = callback.data.split(',')[0]
    now = datetime.now()
    input_history = SearchHistory.create(date=now,
                                         command=callback.data.split(',')[1],
                                         time=now,
                                         user_id=callback.message.chat.id,
                                         )
    user.input_history = input_history
    calendar_mark_up = calendar_markup.create_calendar(now.year, now.month)
    HotelsForYou_Bot.send_message(callback.message.chat.id,
                                  'Введите дату <b>ПРИБЫТИЯ</b>',
                                  reply_markup=calendar_mark_up,
                                  parse_mode='HTML')


@HotelsForYou_Bot.callback_query_handler(func=lambda callback: callback.data == 'history')
def display_search_history(callback):
    for search in SearchHistory.select().where(
            SearchHistory.user_id == callback.message.chat.id and SearchHistory.search_results != 'Null'):
        HotelsForYou_Bot.send_message(chat_id=callback.message.chat.id,
                                      text=f'Фильтр поиска: <b>{search.command}</b>\n'
                                           f'Дата поиска: <b>{search.date}</b>\n'
                                           f'Время поиска: <b>{search.time}</b>\n'
                                           f'\n{search.search_results}',
                                      parse_mode='HTML')

    time.sleep(0.5)
    markup = hotel_search_result_markup.exit_mark_up()
    search = HotelsForYou_Bot.send_message(callback.message.chat.id, 'Желаете продолжить поиск?', reply_markup=markup)
    HotelsForYou_Bot.clear_step_handler(search)


@HotelsForYou_Bot.callback_query_handler(
    func=lambda callback: callback.data in ['proceed',
                                            'best_deal_proceed',
                                            'back'])
def display_result(callback: CallbackQuery) -> None:
    """
    Шаг 8.

    Функция передает данные, введенные пользователем, в функцию hotel_information, которая возвращает список
    с результатом поиска и сохраняет их в атрибут final.data экземпляра класса Users.
    Список состоит из вложенных списков с информацией по каждому отелю, в каждом из которых лежит два элемента:
    список с информацией, которая презентуется пользователю и id отеля, для вывода фотографий.

    Далее функция соединяет информацию в списке в одну единую строку и сохраняет ее в базу данных.

    Далее функция выводит информацию, предназначенную для пользователя, и создает Inline клавиатуру, которая дает
    возможность перейти к следующему отелю, посмотреть фото, перейти к брони и закончить поиск.
    Также функция возвращает пользователя обратно к отелям, после просмотра фотографий.
    :param: callback.data
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)

    if callback.data == 'proceed':

        user.hotel_step = 1

        sticker = HotelsForYou_Bot.send_sticker(callback.message.chat.id, 'CAACAgIAAxkBAAIGAWL0'
                                                                          '-4MCr9PgoBhUGZhgi6AnBCDhAAItAAN4qOYPGMtxPEcwzngpBA')
        user.messages_to_delete.append(sticker.message_id)

        data_for_user = hotel_api_parser.hotel_information(
            destination_id=user.dest_id,
            sort_order=user.sort_order,
            check_in=user.check_in,
            check_out=user.check_out,
            hotel_amount=int(user.hotel_amount))

        user.final_data = data_for_user
        data_for_db = save_result_to_db(data_for_user)
        user.input_history.search_results = data_for_db
        user.input_history.save()

        mark_up = hotel_search_result_markup.hotel_result_mark_up(
            text=str(user.hotel_step),
            prev=False,
            next=True,
            row_width=2,
            hotel_id=user.final_data[user.hotel_step - 1][1]

        )

        for m in user.messages_to_delete:
            HotelsForYou_Bot.delete_message(chat_id=callback.message.chat.id,
                                            message_id=m)
        HotelsForYou_Bot.send_photo(chat_id=callback.message.chat.id,
                                    photo=user.final_data[user.hotel_step - 1][0][-1],
                                    reply_markup=mark_up,
                                    parse_mode='HTML',
                                    caption='\n'.join(user.final_data[user.hotel_step - 1][0][:-1]))

    elif callback.data == 'best_deal_proceed':

        sticker = HotelsForYou_Bot.send_sticker(callback.message.chat.id, 'CAACAgIAAxkBAAIGAWL0'
                                                                          '-4MCr9PgoBhUGZhgi6AnBCDhAAItAAN4qOYPGMtxPEcwzngpBA')
        user.messages_to_delete.append(sticker.message_id)
        user.hotel_step = 1

        data_for_user = hotel_api_parser.hotel_information(
            destination_id=user.dest_id,
            sort_order=user.sort_order,
            check_in=user.check_in,
            check_out=user.check_out,
            hotel_amount=int(user.hotel_amount),
            min_price=int(user.min_price),
            max_price=int(user.max_price),
        )

        user.final_data = data_for_user
        mark_up = hotel_search_result_markup.hotel_result_mark_up(
            text=str(user.hotel_step),
            prev=False,
            next=True,
            row_width=2,
            hotel_id=user.final_data[user.hotel_step - 1][1]
        )
        for m in user.messages_to_delete:
            HotelsForYou_Bot.delete_message(chat_id=callback.message.chat.id,
                                            message_id=m)
        HotelsForYou_Bot.send_photo(chat_id=callback.message.chat.id,
                                    photo=user.final_data[user.hotel_step - 1][0][-1],
                                    reply_markup=mark_up,
                                    parse_mode='HTML',
                                    caption='\n'.join(user.final_data[user.hotel_step - 1][0][:-1]))

    elif callback.data == 'back' and int(user.hotel_amount) > user.hotel_step > 1:
        user.hotel_step += 1
        if user.hotel_step < int(user.hotel_amount):
            mark_up = hotel_search_result_markup.hotel_result_mark_up(
                text=str(user.hotel_step),
                prev=True,
                next=True,
                row_width=3,
                hotel_id=user.final_data[user.hotel_step - 1][1]

            )
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(media=user.final_data[user.hotel_step - 1][0][-1],
                                                                      caption='\n'.join(
                                                                          user.final_data[user.hotel_step - 1][0][:-1]),
                                                                      parse_mode='HTML'),
                                                reply_markup=mark_up)

    elif callback.data == 'back' and user.hotel_step == int(user.hotel_amount):
        mark_up = hotel_search_result_markup.hotel_result_mark_up(
            text=str(user.hotel_step),
            prev=True,
            next=False,
            row_width=2,
            hotel_id=user.final_data[user.hotel_step - 1][1]

        )
        HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                            message_id=callback.message.id,
                                            media=InputMediaPhoto(media=user.final_data[user.hotel_step - 1][0][-1],
                                                                  caption='\n'.join(
                                                                      user.final_data[user.hotel_step - 1][0][:-1]),
                                                                  parse_mode='HTML'),
                                            reply_markup=mark_up)

    elif callback.data == 'back' and user.hotel_step == 1:

        mark_up = hotel_search_result_markup.hotel_result_mark_up(
            text=str(user.hotel_step),
            prev=False,
            next=True,
            row_width=2,
            hotel_id=user.final_data[user.hotel_step - 1][1]

        )
        HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                            message_id=callback.message.id,
                                            media=InputMediaPhoto(media=user.final_data[user.hotel_step - 1][0][-1],
                                                                  caption='\n'.join(
                                                                      user.final_data[user.hotel_step - 1][0][:-1]),
                                                                  parse_mode='HTML'),
                                            reply_markup=mark_up)


@HotelsForYou_Bot.callback_query_handler(func=lambda callback: callback.data in ['next_hotel',
                                                                                 'prev_hotel'])
def scroll_through_results(callback: CallbackQuery) -> None:
    """
    Шаг 8.1

    Функция позволяет переходить к следующего/предыдущему отелю.
    :param callback: callback.data
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)
    if callback.data == 'next_hotel':
        user.hotel_step += 1

        if user.hotel_step < int(user.hotel_amount):

            mark_up = hotel_search_result_markup.hotel_result_mark_up(
                text=str(user.hotel_step),
                prev=True,
                next=True,
                row_width=3,
                hotel_id=user.final_data[user.hotel_step - 1][1]

            )
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(media=user.final_data[user.hotel_step - 1][0][-1],
                                                                      caption='\n'.join(
                                                                          user.final_data[user.hotel_step - 1][0][:-1]),
                                                                      parse_mode='HTML'),
                                                reply_markup=mark_up)
        elif user.hotel_step == int(user.hotel_amount):

            mark_up = hotel_search_result_markup.hotel_result_mark_up(
                text=str(user.hotel_step),
                prev=True,
                next=False,
                row_width=2,
                hotel_id=user.final_data[user.hotel_step - 1][1]

            )
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(media=user.final_data[user.hotel_step - 1][0][-1],
                                                                      caption='\n'.join(
                                                                          user.final_data[user.hotel_step - 1][0][:-1]),
                                                                      parse_mode='HTML'),
                                                reply_markup=mark_up)
    elif callback.data == 'prev_hotel':
        user.hotel_step -= 1

        if user.hotel_step > 1:

            mark_up = hotel_search_result_markup.hotel_result_mark_up(
                text=str(user.hotel_step),
                prev=True,
                next=True,
                row_width=3,
                hotel_id=user.final_data[user.hotel_step - 1][1]

            )
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(media=user.final_data[user.hotel_step - 1][0][-1],
                                                                      caption='\n'.join(
                                                                          user.final_data[user.hotel_step - 1][0][:-1]),
                                                                      parse_mode='HTML'),
                                                reply_markup=mark_up)
        elif user.hotel_step == 1:

            mark_up = hotel_search_result_markup.hotel_result_mark_up(
                text=str(user.hotel_step),
                prev=False,
                next=True,
                row_width=2,
                hotel_id=user.final_data[user.hotel_step - 1][1]

            )
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(media=user.final_data[user.hotel_step - 1][0][-1],
                                                                      caption='\n'.join(
                                                                          user.final_data[user.hotel_step - 1][0][:-1]),
                                                                      parse_mode='HTML'),
                                                reply_markup=mark_up)


@HotelsForYou_Bot.callback_query_handler(func=lambda callback: callback.data in ['get_photos',
                                                                                 'next_photo',
                                                                                 'prev_photo'])
def display_photos(callback: CallbackQuery) -> None:
    """
    Шаг 9.

    Функция передает id отеля в функцию hotel_pictures_load_out, которая выгружает до 20 фотографий отеля и добавляет их
    3 элементом в список с информацией по отелю.
    Также функция позволяет переходить к следующей/предыдущей фотографии.
    :param callback: callback.data
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)
    if callback.data == 'get_photos':
        sticker = HotelsForYou_Bot.send_sticker(callback.message.chat.id, 'CAACAgIAAxkBAAIGAWL0'
                                                                          '-4MCr9PgoBhUGZhgi6AnBCDhAAItAAN4qOYPGMtxPEcwzngpBA')
        user.messages_to_delete = []
        user.messages_to_delete.append(sticker.message_id)
        user.photo_step = 1

        hotel_photos = hotel_api_parser.hotel_pictures_load_out(
            hotel_id=user.final_data[user.photo_step - 1][1]

        )
        user.final_data[user.hotel_step - 1].append(hotel_photos)

        mark_up = hotel_search_result_markup.hotel_photos_mark_up(
            text=user.photo_step,
            prev=False,
            next=True,
            row_width=2)
        for m in user.messages_to_delete:
            HotelsForYou_Bot.delete_message(chat_id=callback.message.chat.id,
                                            message_id=m)
        HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                            message_id=callback.message.id,
                                            media=InputMediaPhoto(
                                                media=user.final_data[user.hotel_step - 1][2][user.photo_step - 1]),
                                            reply_markup=mark_up)

    elif callback.data == 'next_photo':
        user.photo_step += 1

        if user.photo_step < 20:

            mark_up = hotel_search_result_markup.hotel_photos_mark_up(
                text=user.photo_step,
                prev=True,
                next=True,
                row_width=3)
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(
                                                    media=user.final_data[user.hotel_step - 1][2][user.photo_step - 1]),
                                                reply_markup=mark_up)

        elif user.photo_step == 20:

            mark_up = hotel_search_result_markup.hotel_photos_mark_up(
                text=user.photo_step,
                prev=True,
                next=False,
                row_width=2)
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(
                                                    media=user.final_data[user.hotel_step - 1][2][user.photo_step - 1]),
                                                reply_markup=mark_up)

    elif callback.data == 'prev_photo':
        user.photo_step -= 1

        if user.photo_step > 1:

            mark_up = hotel_search_result_markup.hotel_photos_mark_up(
                text=user.photo_step,
                prev=True,
                next=True,
                row_width=3)
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(
                                                    media=user.final_data[user.hotel_step - 1][2][user.photo_step - 1]),
                                                reply_markup=mark_up)

        elif user.photo_step == 1:

            mark_up = hotel_search_result_markup.hotel_photos_mark_up(
                text=user.photo_step,
                prev=False,
                next=True,
                row_width=2)
            HotelsForYou_Bot.edit_message_media(chat_id=callback.message.chat.id,
                                                message_id=callback.message.id,
                                                media=InputMediaPhoto(
                                                    media=user.final_data[user.hotel_step - 1][2][user.photo_step - 1]),
                                                reply_markup=mark_up)


@HotelsForYou_Bot.callback_query_handler(func=lambda callback: callback.data in ['exit',
                                                                                 'see_you_soon_mate'])
def exit_search(callback: CallbackQuery) -> None:
    """
    Шаг 10.

    Функция спрашивает у пользователя, хочет ли он продолжить поиск и, в случае положительного ответа, переносит его к
    начальной функции опроса.
    :param callback: callback.data
    :return: None
    """
    if callback.data == 'exit':
        markup = hotel_search_result_markup.exit_mark_up()
        HotelsForYou_Bot.send_message(callback.message.chat.id, 'Желаете поискать еще?', reply_markup=markup)

    elif callback.data == 'see_you_soon_mate':
        HotelsForYou_Bot.send_message(callback.message.chat.id, 'Приятно было с Вами провести время!\n'
                                                                'Пойду, пожалуй, посплю...😴\n'
                                                                '\nPS Чтобы меня разбудить, набери /start🙃')


@HotelsForYou_Bot.callback_query_handler(func=lambda callback: callback.data in ['input_min_price',
                                                                                 'input_max_price',
                                                                                 'input_max_dist',
                                                                                 'incorrect',
                                                                                 'verify_info'])
def best_deal_search_survey(callback: CallbackQuery) -> None:
    """
    Шаг 7.1.

    Функция запрашивает у пользователя доп информацию для поиска с пользовательскими параметрами: диапазон цен и
    максимальное расстояние от центра.
    Далее, после ввода всей необходимой информации, функция выводит данные на проверку.
    В случае, если при вводе данных была допущена ошибка, функция запрашивает в каком опросе
    (базовом или дополнительном) найдена ошибка и возвращает к начальной функции указанного опроса.
    :param callback: callback.data
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)
    if callback.data == 'input_min_price':
        input_min_price = HotelsForYou_Bot.edit_message_text(chat_id=callback.message.chat.id,
                                                             message_id=callback.message.message_id,
                                                             text='Введите минимальную цену за ночь в отеле💳\n'
                                                                  '\nПример 1: <b>10000</b>\n'
                                                                  'Пример 2: <b>10000.5</b>',
                                                             parse_mode='HTML')
        HotelsForYou_Bot.register_next_step_handler(input_min_price, save_best_deal_survey_info)

    elif callback.data == 'input_max_price':
        input_max_price = HotelsForYou_Bot.edit_message_text(chat_id=callback.message.chat.id,
                                                             message_id=callback.message.message_id,
                                                             text='Введите максимальную цену за ночь в отеле💳\n'
                                                                  '\nПример 1: <b>10000</b>\n'
                                                                  'Пример 2: <b>10000.5</b>',
                                                             parse_mode='HTML')
        HotelsForYou_Bot.register_next_step_handler(input_max_price, save_best_deal_survey_info)

    elif callback.data == 'input_max_dist':
        input_max_distance = HotelsForYou_Bot.edit_message_text(chat_id=callback.message.chat.id,
                                                                message_id=callback.message.message_id,
                                                                text='Введите максимальное расстояние от отеля до центра🏃\n'
                                                                     '\nПример 1: <b>5</b>\n'
                                                                     'Пример 2: <b>5.5</b>', parse_mode='HTML')
        HotelsForYou_Bot.register_next_step_handler(input_max_distance, save_best_deal_survey_info)

    elif callback.data == 'incorrect':
        user.min_price = None
        user.max_price = None
        user.max_distance = None
        mark_up = best_deal_survey_markup.input_parameters(text='В базовой информации⏮',
                                                           callback='from_the_top',
                                                           extra_btn=True,
                                                           extra_text='В дополнительной информации⏪',
                                                           extra_callback='input_min_price')
        HotelsForYou_Bot.edit_message_text(chat_id=callback.message.chat.id,
                                           message_id=callback.message.message_id,
                                           text='Укажите в какой части опроса вы ошиблись:\n',
                                           reply_markup=mark_up,
                                           parse_mode='HTML')

    elif callback.data == 'verify_info':
        markup = verify_information_markup.verify_info(correct_callback='best_deal_proceed',
                                                       incorrect_callback='incorrect')
        HotelsForYou_Bot.edit_message_text(text=
                                           'Спасибо за предоставленную информацию!\n'
                                           'Теперь подведем итоги, чтобы убедиться, что все указано верно:\n'
                                           f'\n▪Вы планируется ваше путешествие в <b>{user.dest_name}</b>\n'
                                           f'▪Вы заезжаете в отель <b>{user.check_in}</b>\n'
                                           f'▪Вы уезжаете из отеля <b>{user.check_out}</b>\n'
                                           f'▪Вы бы хотели увидеть <b>{user.hotel_amount}</b>'
                                           f' варианта(ов).\n'
                                           f'▪Минимальная цена отеля за ночь <b>{user.min_price}</b>\n'
                                           f'▪Максимальная цена отеля за ночь <b>{user.max_price}</b>\n'
                                           f'▪Максимальное расстояние от отеля до центра: <b>{user.max_distance}</b>',
                                           chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           reply_markup=markup, parse_mode='HTML', )


def save_best_deal_survey_info(message: Message) -> None:
    """
    Шаг 7.2

    Функция принимает сообщение от пользователя, предварительно проверяя ее, и сохраняет.
    :param message: объект Message
    :return: None
    """
    user = Users.get_user(message.chat.id)
    if message.text.isdigit() and user.min_price is None:
        user.min_price = message.text
        print(user.min_price)
        print(user.max_price)
        print(user.max_distance)
        markup = best_deal_survey_markup.input_parameters(text='Ввести максимальную цену💳',
                                                          callback='input_max_price')
        HotelsForYou_Bot.send_message(message.chat.id,
                                      text=f'Минимальная цена за ночь в отеле: <b>{user.min_price}</b>',
                                      reply_markup=markup,
                                      parse_mode='HTML'
                                      )
    elif message.text.isdigit() and user.min_price is not None:
        if int(user.min_price) < int(message.text):
            user.max_price = message.text
            print(user.min_price)
            print(user.max_price)
            print(user.max_distance)
            markup = best_deal_survey_markup.input_parameters(text='Ввести максимальную расстояние от центра🏃',
                                                              callback='input_max_dist')
            HotelsForYou_Bot.send_message(message.chat.id,
                                          text=f'Максимальная цена за ночь в отеле: <b>{user.max_price}</b>',
                                          reply_markup=markup,
                                          parse_mode='HTML'
                                          )
        elif int(user.min_price) > int(message.text) and user.max_price is None:
            again = HotelsForYou_Bot.send_message(chat_id=message.chat.id,
                                                  text='Упс...Похоже, что максимальная цена меньше минимальной😬\n'
                                                       'Давайте попробуем еще раз⬇:')
            HotelsForYou_Bot.register_next_step_handler(again, save_best_deal_survey_info)
    elif message.text.isdigit() and user.min_price is not None and user.max_price is not None:
        user.max_distance = message.text
        print(user.min_price)
        print(user.max_price)
        print(user.max_distance)
        markup = best_deal_survey_markup.input_parameters(text='Проверить информацию🧐',
                                                          callback='verify_info')
        HotelsForYou_Bot.send_message(message.chat.id,
                                      text=f'Максимальное расстояние от отеле до центра: <b>{user.max_distance}</b>',
                                      reply_markup=markup,
                                      parse_mode='HTML'
                                      )
    elif not message.text.isdigit():
        print(user.min_price)
        print(user.max_price)
        print(user.max_distance)
        not_digit = HotelsForYou_Bot.send_message(chat_id=message.chat.id,
                                                  text='Упс...Похоже, что Вы ввели буквы, а нужны цифры😬\n'
                                                       'Давайте попробуем еще раз⬇:')

        HotelsForYou_Bot.register_next_step_handler(not_digit, save_best_deal_survey_info)


@HotelsForYou_Bot.callback_query_handler(
    func=lambda callback: 'DAY' in callback.data and Users.get_user(callback.message.chat.id).check_in is None)
def get_check_in_date(callback: CallbackQuery) -> None:
    """
    Шаг 5.

    Функция вытаскивает из callback.data дату, переводит ее в нужный формат и сохраняет информацию.
    Далее функция создает повторно динамический календарь для выбора даты отъезда.
    :param callback: callback.data с датой заезда.
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)
    date = callback.data.split('DAY-')[1]
    check_in = datetime.strptime(date, '%Y-%m-%d')
    user.check_in = str(check_in).split()[0]
    HotelsForYou_Bot.answer_callback_query(callback.id, text="Дата ПРИБЫТИЯ выбрана")
    time.sleep(0.2)
    now = datetime.now()
    calendar_mark_up = calendar_markup.create_calendar(now.year, now.month)
    HotelsForYou_Bot.send_message(callback.message.chat.id, 'Введите дату <b>ОТЪЕЗДА</b>',
                                  reply_markup=calendar_mark_up, parse_mode='HTML')


@HotelsForYou_Bot.callback_query_handler(
    func=lambda callback: 'DAY' in callback.data and Users.get_user(
        callback.message.chat.id).check_out is None)
def get_check_out_date(callback: CallbackQuery) -> None:
    """
    Шаг 6.

    Функция вытаскивает из callback.data дату, переводит ее в нужный формат и сохраняет информацию.
    Далее функция запрашивает у пользователя количество результатов поиска для вывода на экран.
    :param callback: callback.data с датой отъезда.
    :return: None
    """
    user = Users.get_user(callback.message.chat.id)
    date = callback.data.split('DAY-')[1]
    check_out = datetime.strptime(date, '%Y-%m-%d')
    user.check_out = str(check_out).split()[0]
    HotelsForYou_Bot.answer_callback_query(callback.id, text="Дата ОТЪЕЗДА выбрана")
    hotel_amount_request = HotelsForYou_Bot.send_message(chat_id=callback.message.chat.id,
                                                         text='Сколько вариантов вы хотели '
                                                              'бы увидеть? <b>(MAX: 25)</b>',
                                                         parse_mode='HTML')
    HotelsForYou_Bot.register_next_step_handler(hotel_amount_request, hotel_amount)


@HotelsForYou_Bot.callback_query_handler(
    func=lambda callback: 'PREV-MONTH' in callback.data or 'NEXT-MONTH' in callback.data)
def scroll_through_calendar(callback: CallbackQuery) -> None:
    """
    Шаг 4.1.

    Функция дает возможность изменять месяц/год в календаре.
    :param callback: callback.data c указателем в какую сторону листать календарь.
    :return: None
    """
    if "PREV-MONTH" in callback.data:
        year = callback.data.split('-')[2]
        month = callback.data.split('-')[3]
        curr = datetime(int(year), int(month), 1)
        pre = curr - timedelta(days=1)
        HotelsForYou_Bot.edit_message_text(text=callback.message.text,
                                           chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           reply_markup=calendar_markup.create_calendar(int(pre.year), int(pre.month)),
                                           parse_mode='HTML')

    elif "NEXT-MONTH" in callback.data:
        year = callback.data.split('-')[2]
        month = callback.data.split('-')[3]
        curr = datetime(int(year), int(month), 1)
        ne = curr + timedelta(days=31)
        HotelsForYou_Bot.edit_message_text(text=callback.message.text,
                                           chat_id=callback.message.chat.id,
                                           message_id=callback.message.id,
                                           reply_markup=calendar_markup.create_calendar(int(ne.year), int(ne.month)),
                                           parse_mode='HTML')


def hotel_amount(message: Message) -> None:
    """
    Шаг 7.

    Функция принимает сообщение от пользователя, сохраняя данные.
    Далее, в случае, если пользователь выбрал тип поиска с пользовательскими параметрами, функция запрашивает
    дополнительную информацию.
    В обратном случае функция выводит сообщение с данными опроса на проверку..
    :param message: объект Message
    :return: None
    """
    user = Users.get_user(message.chat.id)
    user.input_history.user_id = message.chat.id
    user.input_history.user_name = message.from_user.first_name
    user.input_history.save()
    if message.text.isdigit() and int(message.text) <= 25:
        user = Users.get_user(message.chat.id)
        user.hotel_amount = message.text

        if user.sort_order == 'DISTANCE_FROM_LANDMARK':
            markup = best_deal_survey_markup.input_parameters()
            HotelsForYou_Bot.send_message(message.chat.id, 'Так как Вы выбрали <b>поиск с пользовательскими '
                                                           'параметрами</b>, мне будет необходима дополнительная '
                                                           'информация:\n'
                                                           '\n▪<b>Минимальная цена</b> за ночь в отеле💳\n'
                                                           '▪<b>Максимальная цена</b> за ночь в отеле💳\n'
                                                           '▪<b>Диапазон расстояния</b> от центра'
                                                           'города🏃', parse_mode='HTML', reply_markup=markup)

        else:
            verify_info = verify_information_markup.verify_info()
            HotelsForYou_Bot.send_message(message.chat.id,
                                          text='Спасибо за предоставленную информацию!\n'
                                               'Теперь подведем итоги, чтобы убедиться, что все указано верно:\n'
                                               f'\n▪Вы планируется ваше путешествие в <b>{user.dest_name}</b>\n'
                                               f'▪Вы заезжаете в отель <b>{user.check_in}</b>\n'
                                               f'▪Вы уезжаете из отеля <b>{user.check_out}</b>\n'
                                               f'▪Вы бы хотели увидеть <b>{user.hotel_amount}</b> варианта(ов).',
                                          parse_mode='HTML',
                                          reply_markup=verify_info, )

    elif not message.text.isdigit():
        hotel_amount_request = HotelsForYou_Bot.send_message(message.chat.id,
                                                             'Вы ввели текст, а нужно число...😔'
                                                             'Попробуйте ввести снова.\n'
                                                             'Сколько вариантов вы хотели бы увидеть? (MAX: 25)')
        HotelsForYou_Bot.register_next_step_handler(hotel_amount_request, hotel_amount)

    elif int(message.text) > 25:
        hotel_amount_request = HotelsForYou_Bot.send_message(message.chat.id,
                                                             'Введенное вами кол-во вариантов превышает максимальное '
                                                             'значение...😔'
                                                             'Попробуйте ввести снова.\n'
                                                             'Сколько вариантов вы хотели бы увидеть? (MAX: 25)')
        HotelsForYou_Bot.register_next_step_handler(hotel_amount_request, hotel_amount)
