import requests



class VK:
    """
    класс пользователя ВК
    """
    def __init__(self, access_token, user_id, version='5.131'):

        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

        self.user_update_stop = {}
        # флажки
        self.user_update_stop['all'] = 0
        self.user_update_stop['sex'] = 0
        self.user_update_stop['age_from'] = 0
        self.user_update_stop['age_to'] = 0
        self.user_update_stop['town'] = 0
        self.user_update_stop['status'] = 0
        self.ind = 0
        self.param_search = {}



    def users_info(self):
        """
        функция получения информации о пользователе
        """
        url = 'https://api.vk.com/method/users.get'
        paramss = {'fields':'bdate, sex, home_town, relation'}
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params, **paramss})

        response = response.json()

        try:
            response = response['response']
        except KeyError:
            return []

        return response


    def filefoto(self, user_id):
        """
        функция получения фото
        """
        params = {'owner_id': user_id,
                  'album_id': 'profile',
                  'photo_sizes': '1',
                  'extended': '1'
                  }
        url = 'https://api.vk.com/method/photos.get'
        response = requests.get(url, params={**self.params, **params})
        response = response.json()

        try:
            response = response['response']
        except KeyError:
            return []



        return response

    def search(self, params, count, offset):
        """
        функция поиска людей
        """
        main_param = {'count': count,
                      'offset': offset}

        url = 'https://api.vk.com/method/users.search'
        response = requests.get(url, params={**self.params, **params, **main_param})
        response = response.json()

        try:
            response = response['response']
        except KeyError:
            return []




        return response