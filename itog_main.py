from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# получение токенов

with open('Tokens.txt') as file_object:
    token_user = file_object.readline().strip()
    token_appl = file_object.readline().strip()


#подключение к базе данных


Base = declarative_base()


class Seeker(Base):
    """
    таблица ищущих
    """
    __tablename__ = 'seeker'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), unique=False)
    last_name = sq.Column(sq.String(length=40), unique=False)


class Lover(Base):
    """
    таблица найденных и выведенных на экран
    """
    __tablename__ = 'lover'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), unique=False)
    last_name = sq.Column(sq.String(length=40), unique=False)
    id_seeker = sq.Column(sq.Integer, sq.ForeignKey("seeker.id"), nullable=False, primary_key=True)

    seeker = relationship(Seeker, backref="Seekers")



def create_tables(engine):
    """
    создание таблицы

    """
    Base.metadata.create_all(engine)

# подключение к базе данных

DSN = 'postgresql://postgres:th2AfrM1n7Dp3@localhost:5432/itog'

engine = sq.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

# создание класса бота



def current_keyboard():
    VK_kb = VkKeyboardColor
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Параметры', color=VK_kb.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Поиск', color=VK_kb.PRIMARY)

    return keyboard.get_keyboard()


class VKBot:
    """
    создание бота
    """

    def __init__(self, token):

        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
        self.session_api = self.vk.get_api()
        self.longpoll = VkLongPoll(self.vk)
        self.keyboard = current_keyboard()

    def write_msg(self, user_id: int, message: str, attachment: str = None):
        self.vk.method('messages.send',
                               {'user_id': user_id,
                                'message': message,
                                'random_id': 0,
                                'keyboard': self.keyboard,
                                'attachment': attachment})



#создание класса вконтакте

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
        return response.json()


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
        return response.json()

    def search(self, params):
        """
        функция поиска людей
        """
        main_param = {'count': 1000}

        url = 'https://api.vk.com/method/users.search'
        response = requests.get(url, params={**self.params, **params, **main_param})
        return response.json()




# функция получения параметров поиска

def params_search_func(people_info):
    """
    извлекаем параметры из словаря с параметрами, полученным из рапроса
    """
    if 'sex' in people_info:
        sex = people_info['sex']
    else:
        sex = 0
    if 'home_town' in people_info:
        city = people_info['home_town']
    else:
        city = ''
    relation = people_info['relation']
    if 'bdate' in people_info:
        bdate = people_info['bdate']
    else:
        bdate = '1.1'
    params_search_dict = dict()
    bdate_year = bdate.split('.')
    year = 0
    if len(bdate_year) == 3:
        year = 2023 - int(bdate_year[2])

    if sex == 1:
        params_search_dict['sex'] = 2
    elif sex == 2:
        params_search_dict['sex'] = 1
    if city:
        params_search_dict['hometown'] = city

    if year:
        params_search_dict['age_from'] = year - 2
        params_search_dict['age_to'] = year + 2
    params_search_dict['status'] = relation
    return params_search_dict

# функция проверки параметров

def check_params(params, user_dict, user_id, bot:VKBot):
    """
    проверка парамеров (если флажок равен 0, то все параметры заданы)
    """
    flag = 0
    if params['sex'] == 0:
        flag = 1
        bot.write_msg(user_id, f"Введите свой пол (Пример: пол мужской)")
        user_dict[user_id].user_update_stop['sex'] = 0
    else:
        user_dict[user_id].user_update_stop['sex'] = 1
    if 'age_from' not in params:
        flag = 1
        bot.write_msg(user_id, f"Введите возраст первый (Пример: возраст от 20)")
        user_dict[user_id].user_update_stop['age_from'] = 0
    else:
        user_dict[user_id].user_update_stop['age_from'] = 1
    if 'age_to' not in params:
        flag = 1
        bot.write_msg(user_id, f"Введите возраст второй (Пример: возраст до 25)")
        user_dict[user_id].user_update_stop['age_to'] = 0
    else:
        user_dict[user_id].user_update_stop['age_to'] = 1
    if 'hometown' not in params:
        flag = 1
        bot.write_msg(user_id, f"Введите город (Пример: город Тула)")
        user_dict[user_id].user_update_stop['town'] = 0
    else:
        user_all_dict[user_id].user_update_stop['town'] = 1
    if params['status'] == 0:
        flag = 1
        bot.write_msg(user_id, f"Введите положение (Пример: семейное не женат)")
        user_dict[user_id].user_update_stop['status'] = 0
    else:
        user_dict[user_id].user_update_stop['status'] = 1
    return flag

def parameters(user:VK):
    """
    здесь задаются параметры
    """
    inform_user = user.users_info()
    people = inform_user['response'][0]
    if user.user_update_stop['all'] == 0:
        user.param_search = params_search_func(people)
        user.user_update_stop['all'] = 1
    return people

def family(user:VK, request, bot:VKBot, user_id):
    """
    этой функцией мы задаём семейное положение
    """
    flag_relation = 0

    if user.user_update_stop['status'] == 0:

        if request.lower().endswith('не женат') or request.lower().endswith('не замужем'):
            user.param_search['status'] = 1

        elif request.lower().endswith('есть друг') or request.lower().endswith('есть подруга'):
            user.param_search['status'] = 2

        elif request.lower().endswith('помолвлен') or request.lower().endswith('помолвлена'):
            user.param_search['status'] = 3

        elif request.lower().endswith('женат') or request.lower().endswith('замужем'):
            user.param_search['status'] = 4

        elif request.lower().endswith('всё сложно'):
            user.param_search['status'] = 5

        elif request.lower().endswith('в активном поиске'):
            user.param_search['status'] = 6

        elif request.lower().endswith('влюблён') or request.lower().endswith('влюблена'):
            user.param_search['status'] = 7

        elif request.lower().endswith('в гражданском браке'):
            user.param_search['status'] = 8

        else:
            bot.write_msg(user_id, f"Неверный ввод статуса")

            flag_relation = 1

    return flag_relation


def home_town(user:VK, string_city):
    """
    этой функцией мы задаём город родной
    """
    dict_city = dict()
    city = string_city
    dict_city['hometown'] = city
    user.param_search.update(dict_city)
    user.user_update_stop['town'] = 1


def gender(request, user:VK, bot:VKBot):
    """
    этой функцией мы задаём пол
    """
    gender_dict = dict()
    gender = request.split(' ')
    gender_flag = 0
    if len(gender) == 2 and gender[1] == 'мужской':
        gender_dict['sex'] = 1
        gender_flag = 1
        user.user_update_stop['sex'] = 1
    elif len(gender) == 2 and gender[1] == 'женский':
        gender_dict['sex'] = 2
        gender_flag = 1
        user.user_update_stop['sex'] = 1
    else:
        bot.write_msg(event.user_id, f"Повторите ввод пола")
        user.user_update_stop['sex'] = 0

    if gender_flag == 1:
        user.param_search.update(gender_dict)

    return gender_flag

def age_from(request, user:VK, bot:VKBot, user_dict, user_id):
    """
    этой функцией мы задаём возраст от
    """
    dict_age_from = dict()
    age_from = request.split(' ')
    if (len(age_from) == 3) and (age_from[2].isdigit()):
        dict_age_from['age_from'] = int(age_from[2])
        if ('age_to' in user.param_search) and (80 > dict_age_from['age_from'] > 18):
            if user.param_search['age_to'] > dict_age_from['age_from']:
                user.user_update_stop['age_from'] = 1
                user.param_search.update(dict_age_from)
                flag = check_params(user.param_search, user_dict, user_id, bot)
                if flag == 0:
                    bot.write_msg(event.user_id, f"Параметры успешно созданы, нажмите: поиск")
                    user_flag_in[event.user_id] = 1
            else:

                bot.write_msg(event.user_id, f"Возвраст от неверен")
        elif ('age_to' not in user.param_search) and (
                80 > dict_age_from['age_from'] > 18):
            user.user_update_stop['age_from'] = 1
            user.param_search.update(dict_age_from)
            flag = check_params(user.param_search, user_dict, user_id, bot)
            if flag == 0:
                bot.write_msg(event.user_id, f"Параметры успешно созданы, нажмите: поиск")
                user_flag_in[event.user_id] = 1
    else:
        bot.write_msg(event.user_id, f"Возраст от неверен")

def age_to(request, user:VK, bot:VKBot, user_dict, user_id):
    """
    этой функцией мы задаём возраст до
    """
    dict_age_to = dict()
    age_to = request.split(' ')
    if (len(age_to) == 3) and (age_to[2].isdigit()):
        dict_age_to['age_to'] = int(age_to[2])
        if ('age_from' in user.param_search) and (80 > dict_age_to['age_to'] > 18):
            if user.param_search['age_from'] < dict_age_to['age_to']:
                user.param_search.update(dict_age_to)
                user.user_update_stop['age_to'] = 1

                flag = check_params(user.param_search, user_dict, user_id, bot)

                if flag == 0:
                    bot.write_msg(event.user_id, f"Параметры успешно созданы, нажмите: поиск")
                    user_flag_in[event.user_id] = 1
            else:
                bot.write_msg(event.user_id, f"Возвраст до неверен")
        elif ('age_from' not in user_all_dict[event.user_id].param_search) and (
                80 > dict_age_to['age_to'] > 18):
            user.param_search.update(dict_age_to)
            user.user_update_stop['age_to'] = 1

            flag = check_params(user.param_search, user_dict, user_id, bot)

            if flag == 0:
                bot.write_msg(event.user_id, f"Параметры успешно созданы, введите: поиск класс")
                user_flag_in[event.user_id] = 1
    else:
        bot.write_msg(event.user_id, f"Возвраст до неверен")


# начало программы

botik = VKBot(token_appl)


search_dict = dict()
user_all_dict= dict()
user_flag_in = dict()
all_flag = {}

# подключение к ВК

for event in botik.longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW:
        info = botik.session_api.users.get(users_id=event.user_id)

        if event.to_me:
            request = event.text

            # главный флажок

            all_flag.setdefault(event.user_id, []).append(0)
            if len(all_flag[event.user_id]) == 4:
                all_flag[event.user_id].remove(all_flag[event.user_id][-1])

            # старт бота

            if request.lower() == 'старт':
                all_flag[event.user_id][0] = 1

                botik.write_msg(event.user_id, 'Вы запустили вк_бот. Теперь нажмите "параметры".')




            # создание параметров поиска

            elif request.lower() == 'параметры':
                if all_flag[event.user_id][0] != 1:
                    botik.write_msg(event.user_id, 'Напишите с начала: старт, чтобы начать.')
                else:
                    if event.user_id not in user_all_dict:
                        user_all_dict[event.user_id] = VK(token_user, event.user_id)
                    people = parameters(user_all_dict[event.user_id])
                    q = session.query(Seeker).filter(Seeker.id == people['id'])
                    if not q.all():
                        people_base_seeker = Seeker(id=people['id'], first_name=people['first_name'],
                                                    last_name=people['last_name'])
                        session.add(people_base_seeker)
                        session.commit()
                    if event.user_id not in user_flag_in:
                        user_flag_in[event.user_id] = 0
                    flag = check_params(user_all_dict[event.user_id].param_search, user_all_dict, event.user_id, botik)
                    if flag == 0:
                        botik.write_msg(event.user_id, f"Параметры успешно созданы, нажмите: поиск")
                        user_flag_in[event.user_id] = 1
                    continue

            # задание семейного положения

            elif request.lower().startswith('семейное'):
                if all_flag[event.user_id][0] != 1:
                    botik.write_msg(event.user_id, 'Напишите с начала: старт, чтобы начать.')
                else:
                    if event.user_id in user_all_dict:
                        if user_all_dict[event.user_id].user_update_stop['status'] == 0:
                            flag_relation = family(user_all_dict[event.user_id], request, botik, event.user_id)
                            if flag_relation == 0:
                                user_all_dict[event.user_id].user_update_stop['status'] = 1
                                flag = check_params(user_all_dict[event.user_id].param_search, user_all_dict, event.user_id, botik)
                                if flag == 0:
                                    botik.write_msg(event.user_id, f"Параметры успешно созданы, нажмите: поиск")
                                    user_flag_in[event.user_id] = 1
                        else:
                            botik.write_msg(event.user_id, f"Вы уже ввели семейное положение. Нажмите: параметры")

                    else:
                        botik.write_msg(event.user_id, f"С начал нужно нажать: параметры")



            # задание города
            elif request.lower().startswith('город'):
                if all_flag[event.user_id][0] != 1:
                    botik.write_msg(event.user_id, 'Напишите с начала: старт, чтобы начать.')
                else:
                    if event.user_id in user_all_dict:
                        if user_all_dict[event.user_id].user_update_stop['town'] == 0:
                            home_town(user_all_dict[event.user_id], request)
                            dict_city = dict()
                            city_request = request.split(' ')
                            if len(city_request) == 2:
                                home_town(user_all_dict[event.user_id], city_request[1].title())
                                flag = check_params(user_all_dict[event.user_id].param_search, user_all_dict, event.user_id, botik)
                                if flag == 0:
                                    botik.write_msg(event.user_id, f"Параметры успешно созданы, нажмите: поиск")
                                    user_flag_in[event.user_id] = 1
                            else:
                                botik.write_msg(event.user_id, f"Ввод города некорректен")
                        else:
                            botik.write_msg(event.user_id, f"Вы уже ввели город. Нажмите: параметры")
                    else:
                        botik.write_msg(event.user_id, f"Сначала нужно нажать: параметры")




            # задание пола

            elif request.lower().startswith('пол'):
                if all_flag[event.user_id][0] != 1:
                    botik.write_msg(event.user_id, 'Напишите с начала: старт, чтобы начать.')
                else:
                    if event.user_id in user_all_dict:
                        if user_all_dict[event.user_id].user_update_stop['sex'] == 0:
                            gender_flag = gender(request, user_all_dict[event.user_id], botik)
                            if gender_flag == 1:
                                flag = check_params(user_all_dict[event.user_id].param_search, user_all_dict, event.user_id, botik)
                                if flag == 0:
                                    botik.write_msg(event.user_id, f"Параметры успешно созданы, нажмите: поиск")
                                    user_flag_in[event.user_id] = 1
                        else:
                            botik.write_msg(event.user_id, f"Вы уже ввели пол. Нажмите: параметры")

                    else:
                        botik.write_msg(event.user_id, f"С начал нужно нажать: параметры")




            # возраст от

            elif request.lower().startswith('возраст от'):
                if all_flag[event.user_id][0] != 1:
                    botik.write_msg(event.user_id, 'Напишите с начала: старт, чтобы начать.')
                else:
                    if event.user_id in user_all_dict:
                        if user_all_dict[event.user_id].user_update_stop['age_from'] == 0:
                            age_from(request, user_all_dict[event.user_id], botik, user_all_dict, event.user_id)
                        else:
                            botik.write_msg(event.user_id, f"Возраст от введён. Нажмите: параметры")
                    else:
                        botik.write_msg(event.user_id, f"С начал нужно нажать: параметры")




            # возраст до

            elif request.lower().startswith('возраст до'):
                if all_flag[event.user_id][0] != 1:
                    botik.write_msg(event.user_id, 'Напишите с начала: старт, чтобы начать.')
                else:
                    if event.user_id in user_all_dict:
                        if user_all_dict[event.user_id].user_update_stop['age_to'] == 0:
                            age_to(request, user_all_dict[event.user_id], botik, user_all_dict, event.user_id)
                        else:
                            botik.write_msg(event.user_id, f"Возвраст до уже введён. Нажмите: параметры")

                    else:
                        botik.write_msg(event.user_id, f"С начал нужно нажать: параметры")



            # поиск


            elif request.lower() == "поиск":
                if all_flag[event.user_id][0] != 1:
                    botik.write_msg(event.user_id, 'Напишите с начала: старт, чтобы начать.')
                else:
                    if (event.user_id not in user_flag_in) or (user_flag_in[event.user_id] == 0):
                        user_flag_in[event.user_id] = 0
                        botik.write_msg(event.user_id, 'Поиск невозможен. Нажмите: параметры')
                    elif user_flag_in[event.user_id] == 1:
                        if event.user_id not in search_dict:
                            search_dict[event.user_id] = []
                            parametrs_search = user_all_dict[event.user_id].param_search
                            serch_str = user_all_dict[event.user_id].search(parametrs_search)
                            search_dict[event.user_id] = serch_str['response']['items']
                            serch_res = search_dict[event.user_id]
                            if len(serch_res) == 0:
                                botik.write_msg(event.user_id,
                                                f'К сожалению, ничего не найдено. Измените параметры поиска! Нажмите параметры.')
                                search_dict.pop(event.user_id)
                                user_all_dict.pop(event.user_id)
                                user_flag_in[event.user_id] = 0
                                continue
                        else:
                            serch_res = search_dict[event.user_id]

                        for index in range(user_all_dict[event.user_id].ind, len(serch_res)):
                            if serch_res[index]['is_closed'] == False:
                                if index == len(serch_res) - 1:
                                    botik.write_msg(event.user_id,
                                                    f'Это последний человек. Хотите изменить параметры? Нажмите параметры.')

                                    search_dict.pop(event.user_id)

                                    user_all_dict.pop(event.user_id)
                                    user_flag_in[event.user_id] = 0
                                    break

                                photo = user_all_dict[event.user_id].filefoto(serch_res[index]['id'])

                                if 'response' not in photo:
                                    continue

                                if 'response' in photo:
                                    if photo['response']['count'] == 0:
                                        continue

                                e = session.query(Lover).filter(Lover.id == serch_res[index]['id'],
                                                                Lover.id_seeker == event.user_id)
                                if not e.all():
                                    people_base_lover = Lover(id=serch_res[index]['id'],
                                                              first_name=serch_res[index]['first_name'],
                                                              last_name=serch_res[index]['last_name'],
                                                              id_seeker=event.user_id)

                                    session.add(people_base_lover)

                                    session.commit()
                                else:
                                    continue

                                photo_live = photo['response']['items']
                                like_score = 1
                                comm_score = 3
                                sort_pgoto = lambda x: (x['likes']['count'], x['comments']['count'])[x['likes']['count']* like_score <=x['comments']['count'] * comm_score]
                                new_sort_data = sorted(photo_live, key=sort_pgoto, reverse=True)
                                count = 0

                                string_attach = ''
                                for elements in new_sort_data:

                                    count += 1
                                    string_attach += f'photo{serch_res[index]["id"]}_{elements["id"]},'
                                    if count == 3:
                                        break

                                botik.write_msg(event.user_id, '', attachment = string_attach[:-1])
                                botik.write_msg(event.user_id, f'https://vk.com/id{serch_res[index]["id"]}')

                                user_all_dict[event.user_id].ind = index
                                break
                            if index == len(serch_res) - 1:
                                botik.write_msg(event.user_id,
                                                f'Это последний человек. Хотите изменить параметры? Нажмите параметры.')

                                search_dict.pop(event.user_id)
                                user_all_dict.pop(event.user_id)
                                user_flag_in[event.user_id] = 0
                                break

            # если будет написано что-то, что бот не поёмёт

            else:

                botik.write_msg(event.user_id, "Не понял вашего ответа... Сначала вводите: старт. Потом нажимаете на (параметры). Потом жмуте на (поиск)")

