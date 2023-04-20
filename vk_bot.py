from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType



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
