from vk_bot import VKBot
from vk_user import VK
import time
from base_data import Seeker, Lover

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
        user_dict[user_id].user_update_stop['town'] = 1
    if params['status'] == 0:
        flag = 1
        bot.write_msg(user_id, f"Введите положение (Пример: семейное не женат)")
        user_dict[user_id].user_update_stop['status'] = 0
    else:
        user_dict[user_id].user_update_stop['status'] = 1
    return flag

def parameters(user:VK, dict_user):
    """
    здесь задаются параметры
    """
    people = dict_user
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


def gender(request, user:VK, bot:VKBot, user_id):
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
        bot.write_msg(user_id, f"Повторите ввод пола")
        user.user_update_stop['sex'] = 0

    if gender_flag == 1:
        user.param_search.update(gender_dict)

    return gender_flag

def age_from(request, user:VK, bot:VKBot, user_dict, user_id, user_flag_into):
    """
    этой функцией мы задаём возраст от
    """
    user_flag_into = 0
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
                    bot.write_msg(user_id, f"Параметры успешно созданы, нажмите: поиск")
                    user_flag_into = 1
                    return user_flag_into
                return user_flag_into
            else:

                bot.write_msg(user_id, f"Возвраст от неверен")
                return user_flag_into
        elif ('age_to' not in user.param_search) and (
                80 > dict_age_from['age_from'] > 18):
            user.user_update_stop['age_from'] = 1
            user.param_search.update(dict_age_from)
            flag = check_params(user.param_search, user_dict, user_id, bot)
            if flag == 0:
                bot.write_msg(user_id, f"Параметры успешно созданы, нажмите: поиск")
                user_flag_into = 1
                return user_flag_into
            return user_flag_into
    else:
        bot.write_msg(user_id, f"Возраст от неверен")
        return user_flag_into

def age_to(request, user:VK, bot:VKBot, user_dict, user_id, user_flag_into):
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
                    bot.write_msg(user_id, f"Параметры успешно созданы, нажмите: поиск")
                    user_flag_into = 1
                    return user_flag_into
                return user_flag_into
            else:
                bot.write_msg(user_id, f"Возвраст до неверен")
                return user_flag_into
        elif ('age_from' not in user_dict.param_search) and (
                80 > dict_age_to['age_to'] > 18):
            user.param_search.update(dict_age_to)
            user.user_update_stop['age_to'] = 1

            flag = check_params(user.param_search, user_dict, user_id, bot)

            if flag == 0:
                bot.write_msg(user_id, f"Параметры успешно созданы, нажмите: поиск")
                user_flag_into = 1
                return user_flag_into
            return user_flag_into


    else:
        bot.write_msg(user_id, f"Возвраст до неверен")
        return user_flag_into


def search_of_photo(elem, user_id, user:VK, bot:VKBot, session, index):
    photo = user.filefoto(elem['id'])
    time.sleep(0.3)


    if photo.status_code == 200 and 'response' in photo.json():
        photo_one = photo.json()

        if photo_one['response']['count'] != 0:


            e = session.query(Lover).filter(Lover.id == elem['id'],
                                               Lover.id_seeker == user_id)

            if not e.all():
                people_base_lover = Lover(id=elem['id'],
                                          first_name=elem['first_name'],
                                          last_name=elem['last_name'],
                                          id_seeker=user_id)

                session.add(people_base_lover)

                session.commit()



                photo_live = photo_one['response']['items']
                like_score = 1
                comm_score = 3
                sort_pgoto = lambda x: (x['likes']['count'], x['comments']['count'])[
                    x['likes']['count'] * like_score <= x['comments']['count'] * comm_score]
                new_sort_data = sorted(photo_live, key=sort_pgoto, reverse=True)
                count = 0

                string_attach = ''
                for elements in new_sort_data:

                    count += 1
                    string_attach += f'photo{elem["id"]}_{elements["id"]},'
                    if count == 3:
                        break

                bot.write_msg(user_id, '', attachment=string_attach[:-1])
                bot.write_msg(user_id, f'https://vk.com/id{elem["id"]}')

                user.ind = index + 1
                return 1
    else:
        bot.write_msg(user_id,
                                f'Сервер не отвечает')
        return 0
