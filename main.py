import telebot
import requests
from telebot import types

TOKEN = ''
ALLOWED_USER = [405018954, 5109080807, 1464466803]
bot = telebot.TeleBot(TOKEN)
APIURL = 'http://localhost/php/server.php'
selected_hall = None
selected_SPL = None
lamp = '?mod=set&id=3&cmd=fire_cue&uuid=urn:uuid:b245a26c-07d2-2202-8694-e79cd36420ff&name=LAMP_OFF'

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in ALLOWED_USER:
        bot.reply_to(message, f'Вы не авторизованы Ваш ID: {user_id}')
        return
    else:
        bot.send_message(message.chat.id, f'Добро пожаловать! Ваш ID: {user_id}')
        main_menu(message)

@bot.callback_query_handler(func=lambda call: True)
def inline_btn_shows(call):
    uuid = call.data
    bot.delete_message(call.message.chat.id, call.message.message_id)
    res = requests.get(f'{APIURL}?mod=set&id={selected_hall}&cmd=load_content&uuid={uuid}&conttype=SPL')
    if res.json()['result'] == 'ok':
        bot.send_message(call.message.chat.id, f'Фильм загружен в {selected_hall} зале пользователем {call.from_user.id}')
    else:
        bot.send_message(call.message.chat.id, f'{selected_hall}Ошибка выполнения запроса{uuid}')

def main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('1 зал')
    itembtn2 = types.KeyboardButton('2 зал')
    itembtn3 = types.KeyboardButton('3 зал')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Выберите зал:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['1 зал', '2 зал', '3 зал'])
def select_hall(message):
    global selected_hall
    selected_hall = message.text.split()[0]
    hall_menu(message)

def hall_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Управление светом')
    itembtn2 = types.KeyboardButton('Управление показом')
    itembtn3 = types.KeyboardButton('к выбору залов')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Управление светом')
def light_control(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Включить')
    itembtn2 = types.KeyboardButton('Выключить')
    itembtn3 = types.KeyboardButton('к выбору залов')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Управление показом')
def show_control(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Остановить показ')
    itembtn2 = types.KeyboardButton('Выбрать фильм')
    itembtn3 = types.KeyboardButton('Воспроизвести выбранный фильм')
    itembtn4 = types.KeyboardButton('к выбору залов')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
def req_tms(mod, hall, cmd, uuid, cmdname):
    url = APIURL
    params = {'mod': mod, 'id': hall, 'cmd': cmd, 'uuid': uuid, 'name': cmdname}
    # t = Timer(delay, request.get(url, params=params))
    # t.start()
    response = requests.get(url, params=params)
    return response
def show_get_list(hall):
    shows = requests.get(f'{APIURL}?mod=get&id=all&ids={hall}&cmd=get_shows_db')
    return shows.json()

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    action = message.text.lower()
    global selected_hall
    if action == 'к выбору залов':
        main_menu(message)
    elif action == 'включить':
        if selected_hall != None and selected_hall != '1':
            response = req_tms('set', selected_hall, 'fire_cue', '', 'CBET_ON')
            if response.json()['result'] == 'ok':
                bot.send_message(message.chat.id, f'Свет включен в {selected_hall} зале пользователем {user_id}')
                main_menu(message)
            else:
                bot.send_message(message.chat.id, f'{selected_hall}Ошибка выполнения запроса{response.text}')
        elif selected_hall == '1':
            response = req_tms('set', selected_hall, 'fire_cue', 'urn:uuid:12979c32-14c9-4ad5-8897-cf01fe4d918e', 'CBET_TOP_ON')
            if response.json()['result'] == 'ok':
                bot.send_message(message.chat.id, f'Свет включен в {selected_hall} зале пользователем {user_id}')
                main_menu(message)
            else:
                bot.send_message(message.chat.id, f'{selected_hall}Ошибка 1 выполнения запроса {response.text}')
        else:
            bot.send_message(message.chat.id, f'Зал не выбран')
    elif action == 'выключить':
        if selected_hall != None and selected_hall != '1':
            response = req_tms('set', selected_hall, 'fire_cue', '', 'CBET_OFF')
            if response.json()['result'] == 'ok':
                bot.send_message(message.chat.id, f'Свет выключен в {selected_hall} зале пользователем {user_id}')
                main_menu(message)
            else:
                bot.send_message(message.chat.id, 'Ошибка выполнения запроса')
        elif selected_hall == '1':
            response = req_tms('set', selected_hall, 'fire_cue', 'urn:uuid:3b3522d2-b7c8-46ef-a794-44c89bab2b9c', 'CBET_TOP_OFF')
            response1 = req_tms('set', selected_hall, 'fire_cue', 'urn:uuid:b1a796f6-9643-491f-bf84-4405d4509690', 'CBET_SIDE_OFF')
            if response.json()['result'] == 'ok':
                bot.send_message(message.chat.id, f'Свет выключен в {selected_hall} зале пользователем {user_id}')
                main_menu(message)
            else:
                bot.send_message(message.chat.id, 'Ошибка выполнения запроса')
        else:
            bot.send_message(message.chat.id, f'Зал не выбран')
    elif action == 'остановить показ':
        if selected_hall != None:
            response = req_tms('set', selected_hall, 'stop', '', '')
            if response.json()['result'] == 'ok':
                bot.send_message(message.chat.id, f'Показ остановлен в {selected_hall} зале пользователем {user_id}')
                main_menu(message)
            else:
                bot.send_message(message.chat.id, 'Ошибка выполнения запроса')
        else:
            bot.send_message(message.chat.id, f'Зал не выбран')
    elif action == 'воспроизвести выбранный фильм':
        if selected_hall != None:
            response = req_tms('set', selected_hall, 'play', '', '')
            if response.json()['result'] == 'ok':
                bot.send_message(message.chat.id, f'Зпущено шоу в {selected_hall} зале пользователем {user_id}')
                main_menu(message)
            else:
                bot.send_message(message.chat.id, 'Ошибка выполнения запроса')
        else:
            bot.send_message(message.chat.id, f'Зал не выбран')
    elif action == 'выбрать фильм':
        if selected_hall != None:
            shows = show_get_list(selected_hall)
            buttons = [
                [telebot.types.InlineKeyboardButton(show['name'], callback_data=show['uuid'])]

                for show in shows['data']
            ]
            keyboard = types.InlineKeyboardMarkup(buttons)
            bot.send_message(message.chat.id, 'Выберите фильм', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда')
bot.polling()
