from vk_user import VK
import time
from vk_api.longpoll import VkEventType
from base_data import Seeker, Lover, create_base_data
from tok import token_user, token_appl

from vk_bot import VKBot
import logik_interface as log

# начало программы

def main():

    botik = VKBot(token_appl)

    session_bd = create_base_data()

    search_dict = dict()
    user_all_dict= dict()
    user_flag_in = dict()
    all_flag = {}
    count_search = 150
    offset = 0
    flag_search_off = {}

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
                        flag_search_off.setdefault(event.user_id, 0)

                        inform_user = user_all_dict[event.user_id].users_info()
                        if inform_user.status_code == 200 and 'response' in inform_user.json():

                            inform_user = inform_user.json()
                            inform = inform_user['response'][0]
                            people = log.parameters(user_all_dict[event.user_id], inform)

                            q = session_bd.query(Seeker).filter(Seeker.id == people['id'])
                            if not q.all():
                                people_base_seeker = Seeker(id=people['id'], first_name=people['first_name'],
                                                            last_name=people['last_name'])
                                session_bd.add(people_base_seeker)
                                session_bd.commit()
                            if event.user_id not in user_flag_in:
                                user_flag_in[event.user_id] = 0
                            flag = log.check_params(user_all_dict[event.user_id].param_search, user_all_dict, event.user_id, botik)
                            if flag == 0:
                                botik.write_msg(event.user_id, f"Параметры успешно созданы, нажмите: поиск")
                                user_flag_in[event.user_id] = 1
                            continue
                        else:
                            botik.write_msg(event.user_id, f"Сервер не отвечает")
                            continue

                # задание семейного положения

                elif request.lower().startswith('семейное'):
                    if all_flag[event.user_id][0] != 1:
                        botik.write_msg(event.user_id, 'Напишите с начала: старт, чтобы начать.')
                    else:
                        if event.user_id in user_all_dict:
                            if user_all_dict[event.user_id].user_update_stop['status'] == 0:
                                flag_relation = log.family(user_all_dict[event.user_id], request, botik, event.user_id)
                                if flag_relation == 0:
                                    user_all_dict[event.user_id].user_update_stop['status'] = 1
                                    flag = log.check_params(user_all_dict[event.user_id].param_search, user_all_dict, event.user_id, botik)
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
                                # log.home_town(user_all_dict[event.user_id], request)
                                # dict_city = dict()
                                city_request = request.split(' ')
                                if len(city_request) == 2:
                                    log.home_town(user_all_dict[event.user_id], city_request[1].title())
                                    flag = log.check_params(user_all_dict[event.user_id].param_search, user_all_dict, event.user_id, botik)
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
                                gender_flag = log.gender(request, user_all_dict[event.user_id], botik, event.user_id)
                                if gender_flag == 1:
                                    flag = log.check_params(user_all_dict[event.user_id].param_search, user_all_dict, event.user_id, botik)
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
                                log.age_from(request, user_all_dict[event.user_id], botik, user_all_dict, event.user_id, user_flag_in[event.user_id])
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
                                log.age_to(request, user_all_dict[event.user_id], botik, user_all_dict, event.user_id, user_flag_in[event.user_id])
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
                                if flag_search_off[event.user_id] == 0:
                                    offset = 0
                                serch_str = user_all_dict[event.user_id].search(parametrs_search, count_search, offset)
                                if serch_str.status_code == 200 and 'response' in serch_str.json():
                                    serch_str = serch_str.json()
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
                                    botik.write_msg(event.user_id,
                                                    f'Сервер не отвечает')
                                    continue

                            else:
                                serch_res = search_dict[event.user_id]

                            for index in range(user_all_dict[event.user_id].ind, len(serch_res)):



                                if serch_res[index]['is_closed'] == False:
                                    if index == len(serch_res) - 1 and len(serch_res) != count_search:
                                        botik.write_msg(event.user_id,
                                                        f'Это последний человек. Хотите изменить параметры? Нажмите параметры.')

                                        search_dict.pop(event.user_id)

                                        user_all_dict.pop(event.user_id)
                                        user_flag_in[event.user_id] = 0
                                        flag_search_off[event.user_id] = 0
                                        break
                                    elif index == len(serch_res) - 1 and len(serch_res) == count_search:
                                        botik.write_msg(event.user_id,
                                                        f'Нажмите ещё раз поиск')

                                        search_dict.pop(event.user_id)
                                        offset += count_search
                                        user_all_dict[event.user_id].ind = 0
                                        flag_search_off[event.user_id] = 1


                                        break


                                    photo = user_all_dict[event.user_id].filefoto(serch_res[index]['id'])
                                    time.sleep(0.2)

                                    if photo.status_code == 200 and 'response' in photo.json():
                                        photo_one = photo.json()


                                        if photo_one['response']['count'] == 0:
                                            continue

                                        super_list = []

                                        e = session_bd.query(Lover).filter(Lover.id == serch_res[index]['id'],
                                                                          Lover.id_seeker == event.user_id)


                                        super_list.append([elem for elem in e.all()])

                                        if not e.all():
                                            people_base_lover = Lover(id=serch_res[index]['id'],
                                                                        first_name=serch_res[index]['first_name'],
                                                                        last_name=serch_res[index]['last_name'],
                                                                        id_seeker=event.user_id)

                                            session_bd.add(people_base_lover)

                                            session_bd.commit()




                                        else:
                                            super_list.clear()
                                            continue

                                        photo_live = photo_one['response']['items']
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


                                        user_all_dict[event.user_id].ind = index + 1
                                        break
                                    else:
                                        botik.write_msg(event.user_id,
                                                        f'Сервер не отвечает')
                                        continue

                                if index == len(serch_res) - 1 and len(serch_res) != count_search:
                                    botik.write_msg(event.user_id,
                                                    f'Это последний человек. Хотите изменить параметры? Нажмите параметры.')

                                    search_dict.pop(event.user_id)

                                    user_all_dict.pop(event.user_id)
                                    user_flag_in[event.user_id] = 0
                                    flag_search_off[event.user_id] = 0
                                    break
                                elif index == len(serch_res) - 1 and len(serch_res) == count_search:
                                    botik.write_msg(event.user_id,
                                                    f'Нажмите ещё раз поиск')

                                    search_dict.pop(event.user_id)
                                    offset += count_search
                                    user_all_dict[event.user_id].ind = 0
                                    flag_search_off[event.user_id] = 1

                                    break

                # если будет написано что-то, что бот не поёмёт

                else:

                    botik.write_msg(event.user_id, "Не понял вашего ответа... Сначала вводите: старт. Потом нажимаете на (параметры). Потом жмуте на (поиск)")


if __name__ == "__main__":
    main()