import requests
import json


def data_request_to_api(url, headers, querystring):
    try:
        request = requests.get(url=url, headers=headers, params=querystring)
        if request.status_code == requests.codes.ok:
            data = json.loads(request.text)
            return data
    except Exception as e:
        print('Ошибка API')
        print(e)
        return None
