from request_function import request_function
from config_data import config

headers = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}


def destination_id_verification(destination):
    destination_id_data = request_function.data_request_to_api(
        url="https://hotels4.p.rapidapi.com/locations/v2/search",
        querystring={"query": destination, "locale": "en_US", "currency": "RUB"},
        headers=headers)
    destination_id = destination_id_data['suggestions'][0]['entities']
    city_neighborhoods = []
    for data in destination_id:
        city_neighborhoods.append(
            {
                'neighborhood_name': data['name'],
                'neighborhood_id': data['destinationId']
            }
        )

    return city_neighborhoods


def hotel_information(destination_id, sort_order, check_in, check_out, hotel_amount, page_number='1', min_price=None,
                      max_price=None):
    properties_data = {}
    if min_price is None:
        properties_data = request_function.data_request_to_api(url="https://hotels4.p.rapidapi.com/properties/list",
                                                               querystring={"destinationId": destination_id,
                                                                            "pageNumber": page_number,
                                                                            "pageSize": '25', "checkIn": check_in,
                                                                            "checkOut": check_out, "adults1": '1',
                                                                            "sortOrder": sort_order, "locale": "en_US",
                                                                            "currency": "RUB"},
                                                               headers=headers)
    else:
        properties_data = request_function.data_request_to_api(url="https://hotels4.p.rapidapi.com/properties/list",
                                                               querystring={"destinationId": destination_id,
                                                                            "pageNumber": "1", "pageSize": "25",
                                                                            "checkIn": check_in,
                                                                            "checkOut": check_out, "adults1": "1",
                                                                            "priceMin": min_price,
                                                                            "priceMax": max_price,
                                                                            "sortOrder": sort_order,
                                                                            "locale": "en_US", "currency": "RUB"},
                                                               headers=headers)
    hotels_data = properties_data['data']['body']['searchResults']['results']

    data_for_user = []

    for data in hotels_data[:hotel_amount]:
        if "guestReviews" not in data and "streetAddress" in data['address']:
            data_for_user.append(
                [[f'<b>{data["name"]}</b>\n',
                  f'📍Адрес отеля: {data["address"]["streetAddress"]}',
                  f'⭐Рейтинг отеля: {data["starRating"]}',
                  f'⭐Рейтинг гостей: информация не найдена',
                  f'🏃Расстояние до центра города: {data["landmarks"][0]["distance"]}',
                  f'💳Цена за ночь: {data["ratePlan"]["price"]["current"]}',
                  data['optimizedThumbUrls']["srpDesktop"]],
                 f'{data["id"]}']
            )

        elif "streetAddress" not in data['address'] and "guestReviews" in data:
            data_for_user.append(
                [[f'<b>{data["name"]}</b>\n',
                  f'📍Адрес отеля: {"locality"}',
                  f'⭐Рейтинг отеля: {data["starRating"]}',
                  f'⭐Рейтинг гостей: {data["guestReviews"]["rating"]}',
                  f'🏃Расстояние до центра города: {data["landmarks"][0]["distance"]}',
                  f'💳Цена за ночь: {data["ratePlan"]["price"]["current"]}',
                  data['optimizedThumbUrls']["srpDesktop"]],
                 f'{data["id"]}']
            )

        elif "guestReviews" not in data and "streetAddress" not in data['address']:
            data_for_user.append(
                [[f'<b>{data["name"]}</b>\n',
                  f'📍Адрес отеля: {"locality"}',
                  f'⭐Рейтинг отеля: {data["starRating"]}',
                  f'⭐Рейтинг гостей: информация не найдена',
                  f'🏃Расстояние до центра города: {data["landmarks"][0]["distance"]}',
                  f'💳Цена за ночь: {data["ratePlan"]["price"]["current"]}',
                  data['optimizedThumbUrls']["srpDesktop"]],

                 f'{data["id"]}']

            )

        else:
            data_for_user.append(
                [[f'<b>{data["name"]}</b>\n',
                  f'📍Адрес отеля: {data["address"]["streetAddress"]}',
                  f'⭐Рейтинг отеля: {data["starRating"]}',
                  f'⭐Рейтинг гостей: {data["guestReviews"]["rating"]}',
                  f'🏃Расстояние до центра города: {data["landmarks"][0]["distance"]}',
                  f'💳Цена за ночь: {data["ratePlan"]["price"]["current"]}',
                  data['optimizedThumbUrls']["srpDesktop"]],
                 f'{data["id"]}'

                 ]

            )

    return data_for_user


# a = hotel_information('10818945', 'DISTANCE_FROM_LANDMARK', '2022-08-19', '2022-08-25', min_price=20000,
# max_price=30000, hotel_amount=10) print(a)


def hotel_pictures_load_out(hotel_id, image_amount=20):
    properties_data = request_function.data_request_to_api(
        url="https://hotels4.p.rapidapi.com/properties/get-hotel-photos",
        querystring={"id": hotel_id},
        headers=headers)

    image_data = properties_data['hotelImages']
    return [image["baseUrl"].replace("{size}", "y") for image in image_data[:image_amount]]
