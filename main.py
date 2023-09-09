import telebot
from telebot import types
import sqlite3
import time

#---Набор данных для Телеграм бота---
bot = telebot.TeleBot('6631263920:AAGeE6bwL3AFTqTRzkeq2iFALEZtYxdC51U')
ADRES_Base = 6445576278 #Готовый id
ADRES_Premium = 6472769351 #Готовый id
ADRES_VIP = 6252560106 #Готовый id НОМЕР: +7 (707) 325 6100

#---Набор переменных необходимых для разделения пользователей
User_level = -1
global Result
Result = False

#---Стартовая функция---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Напишите /homework что бы передать задание. '
                                      'Работает только если вы есть в одном из каналов Math5Base, Math5Premium или Math5VIP')

#---Тестовая функция---
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, message.chat.id)

@bot.message_handler(commands=['timecontrol'])
def timecontrol(message):
    VIP_Time_Control()

#---Тестовая функция---
@bot.message_handler(commands=['insertnull'])
def insert(message):
    ToDataBase_ALL(0, -1, 0, 0, 0, 0)
    bot.send_message(message.chat.id, "Да")

def VIP_Time_Control():
    sent_message = bot.send_message(ADRES_VIP, "Проверка на время")

    date_message_list = FromDataBase_TimeMessage()
    for date_message in date_message_list:
        if(sent_message.date >= date_message[0] + 60 * 60 * 15):
            task_id = FromDataBase_Task_ID_byTime(date_message[0])
            messageAdmin = FromDataBase_MessageAdmin_ID_by_Task_ID(task_id)
            bot.send_message(ADRES_VIP, f"Задание #⃣{task_id} не выполнено. Прошло больше 15 часов.", reply_to_message_id=messageAdmin)

    bot.delete_message(ADRES_VIP, sent_message.message_id)

    time.sleep(15*60)
    VIP_Time_Control()

#---Проверка на нахождение пользователя в каналах---
@bot.message_handler(commands=['homework'])
def if_in_channels(message): #Проверка на наличие пользователя в каналах Math5VIP, Math5Premium, Math5Base

    global User_level
    global Result

    User_level = -1

    chat_member = bot.get_chat_member(-1001895565286, message.from_user.id)
    if chat_member.status in ['member', 'administrator', 'creator']: #Проверка на Base
        User_level = 2

    chat_member = bot.get_chat_member(-1001516182246, message.from_user.id)
    if chat_member.status in ['member', 'administrator', 'creator']:  # Проверка на Premium
        User_level = 1

    chat_member = bot.get_chat_member(-1001818638802, message.from_user.id)
    if chat_member.status in ['member', 'administrator', 'creator']: #Проверка на VIP
        User_level = 0

    if(User_level == 0 or User_level == 1 or User_level == 2):
        bot.send_message(message.chat.id, "Проверка пройдена✅")
        bot.send_message(message.chat.id, "Скиньте домашнее задание одним сообщением или разделите его на части, указав номер.")
        bot.send_message(message.chat.id,"Бот принимает текстовые или фото сообщения с текстом.")
        Result = True
    else:
        bot.send_message(message.chat.id, "❌Вы не в каналах. Зайти в каналы можно через чат бот @Matesha_online_ChannelsBot. Если вы в каналах, то напишите <a href='https://t.me/azamat_kireyev'>администратору</a> или <a href='https://t.me/Kireyev_Abai'>тех поддержке</a>.", parse_mode='html')

#---ДЛЯ АДМИНОВ, проверка невыполненых заданий---
@bot.message_handler(commands=['list'])
def list(message):
    if(message.chat.id == ADRES_VIP):
        bot.send_message(ADRES_VIP, "VIP задания, которые не опубликованы:")
        DB_list = FromDataBase_Task_ID_VIP_notAnswer()
        list_var = 'Задания:'
        for CASH in DB_list:
            bot.send_message(ADRES_VIP, f"#⃣{CASH[0]}", reply_to_message_id=FromDataBase_MessageAdmin_ID_by_Task_ID(CASH[0]))

    if (message.chat.id == ADRES_Premium):
        bot.send_message(ADRES_Premium, "Premium задания, которые не опубликованы:")
        DB_list = FromDataBase_Task_ID_Premium_notAnswer()
        list_var = 'Задания:'
        for CASH in DB_list:
            list_var = list_var + "#⃣" + str(CASH[0]) + ", "
        bot.send_message(ADRES_Premium, list_var)

    if (message.chat.id == ADRES_Base):
        bot.send_message(ADRES_Base, "Base задания, которые не опубликованы:")
        DB_list = FromDataBase_Task_ID_BASE_notAnswer()
        list_var = 'Задания:'
        for CASH in DB_list:
            list_var = list_var + "#⃣" + str(CASH[0]) + ", "
        bot.send_message(ADRES_Base, list_var)


#---Фото-сообщение которое готовяться к отправке---
@bot.message_handler(content_types=['photo'])
def Send_Photo(message):
    global Result

    if(Result):

        # Подготовка к SQL запросам
        var_ID = FromDataBase_ID_LAST() + 1
        var_Task_ID = FromDataBase_Task_ID_LAST()
        var_Task_ID = var_Task_ID % 1000000 + 1
        var_ChatUser_ID = message.chat.id
        var_Answer = 0

        markup = types.InlineKeyboardMarkup()

        if (User_level == 0):
            markup.add(types.InlineKeyboardButton("Опубликовано", callback_data="HAS_ANSWER_VIP_PHOTO"))
            photo = message.photo[-1]
            sent_message = bot.send_photo(ADRES_VIP, photo.file_id, caption=f"🌟VIP Заданиe🌟 #⃣{var_Task_ID+3000000}\n📝{message.caption}\n❌Не Выполнено❌", reply_markup=markup)

            var_MessageAdmin_ID = sent_message.message_id
            bot.send_message(message.chat.id, f"Отправлено, ожидайте🕐. Номер вашего задания: #⃣{var_Task_ID + 3000000}")

            ToDataBase_ALL(var_ID, var_Task_ID + 3000000, var_MessageAdmin_ID, var_ChatUser_ID, var_Answer, message.date)

        if (User_level == 1):
            markup.add(types.InlineKeyboardButton("Опубликовано", callback_data="HAS_ANSWER_PREMIUM_PHOTO"))
            photo = message.photo[-1]
            sent_message = bot.send_photo(ADRES_Premium, photo.file_id, caption=f"⭐️Premium Заданиe⭐️ #⃣{var_Task_ID+2000000}\n📝{message.caption}\n❌Не Выполнено❌", reply_markup=markup)

            var_MessageAdmin_ID = sent_message.message_id
            bot.send_message(message.chat.id, f"Отправлено, ожидайте🕐. Номер вашего задания: #⃣{var_Task_ID + 2000000}")

            ToDataBase_ALL(var_ID, var_Task_ID + 2000000, var_MessageAdmin_ID, var_ChatUser_ID, var_Answer, message.date)

        if (User_level == 2):
            markup.add(types.InlineKeyboardButton("Опубликовано", callback_data="HAS_ANSWER_BASE_PHOTO"))
            photo = message.photo[-1]
            sent_message = bot.send_photo(ADRES_Base, photo.file_id, caption=f"5️⃣Base Заданиe5️⃣ #⃣{var_Task_ID+1000000}\n📝{message.caption}\n❌Не Выполнено❌", reply_markup=markup)

            var_MessageAdmin_ID = sent_message.message_id
            bot.send_message(message.chat.id, f"Отправлено, ожидайте🕐. Номер вашего задания: #⃣{var_Task_ID + 1000000}")

            ToDataBase_ALL(var_ID, var_Task_ID + 1000000, var_MessageAdmin_ID, var_ChatUser_ID, var_Answer, message.date)

        Result = False


#---CallBack, Кнопка "Выполнено"---
@bot.callback_query_handler(func=lambda callback:True)
def callback_message(callback):

    #CALL_BACK для Текстовых сообщений
    if(callback.data == 'HAS_ANSWER_VIP'):
        new_text = callback.message.text.replace("❌Не Выполнено❌", "")
        bot.edit_message_text(f"{new_text}✅Выполнено✅", ADRES_VIP, callback.message.message_id)
        chat_ID = FromDataBase_Chat_ID(callback.message.message_id)
        task_id = FromDataBase_Task_ID(callback.message.message_id)
        UpdateDataBase_Answer(callback.message.message_id)
        bot.send_message(chat_ID, f"✅Ваше задание #⃣{task_id} выполнено. Ответ уже в каналах")

    if(callback.data == 'HAS_ANSWER_PREMIUM'):
        new_text = callback.message.text.replace("❌Не Выполнено❌", "")
        bot.edit_message_text(f"{new_text}✅Выполнено✅", ADRES_Premium, callback.message.message_id)
        chat_ID = FromDataBase_Chat_ID(callback.message.message_id)
        task_id = FromDataBase_Task_ID(callback.message.message_id)
        UpdateDataBase_Answer(callback.message.message_id)
        bot.send_message(chat_ID, f"✅Ваше задание #⃣{task_id} выполнено. Ответ уже в каналах")

    if(callback.data == 'HAS_ANSWER_BASE'):
        new_text = callback.message.text.replace("❌Не Выполнено❌", "")
        bot.edit_message_text(f"{new_text}✅Выполнено✅", ADRES_Base, callback.message.message_id)
        chat_ID = FromDataBase_Chat_ID(callback.message.message_id)
        task_id = FromDataBase_Task_ID(callback.message.message_id)
        UpdateDataBase_Answer(callback.message.message_id)
        bot.send_message(chat_ID, f"✅Ваше задание #⃣{task_id} выполнено. Ответ уже в каналах")

    if (callback.data == 'HAS_ANSWER_VIP_PHOTO'):
        new_text = callback.message.caption.replace("❌Не Выполнено❌", "")
        bot.edit_message_caption(f"{new_text}✅Выполнено✅", ADRES_VIP, callback.message.message_id)
        chat_ID = FromDataBase_Chat_ID(callback.message.message_id)
        task_id = FromDataBase_Task_ID(callback.message.message_id)
        UpdateDataBase_Answer(callback.message.message_id)
        bot.send_message(chat_ID, f"✅Ваше задание #⃣{task_id} выполнено. Ответ уже в каналах")

    if (callback.data == 'HAS_ANSWER_PREMIUM_PHOTO'):
        new_text = callback.message.caption.replace("❌Не Выполнено❌", "")
        bot.edit_message_caption(f"{new_text}✅Выполнено✅", ADRES_Premium, callback.message.message_id)
        chat_ID = FromDataBase_Chat_ID(callback.message.message_id)
        task_id = FromDataBase_Task_ID(callback.message.message_id)
        UpdateDataBase_Answer(callback.message.message_id)
        bot.send_message(chat_ID, f"✅Ваше задание #⃣{task_id} выполнено. Ответ уже в каналах")

    if (callback.data == 'HAS_ANSWER_BASE_PHOTO'):
        new_text = callback.message.caption.replace("❌Не Выполнено❌", "")
        bot.edit_message_caption(f"{new_text}✅Выполнено✅", ADRES_Base, callback.message.message_id)
        chat_ID = FromDataBase_Chat_ID(callback.message.message_id)
        task_id = FromDataBase_Task_ID(callback.message.message_id)
        UpdateDataBase_Answer(callback.message.message_id)
        bot.send_message(chat_ID, f"✅Ваше задание #⃣{task_id} выполнено. Ответ уже в каналах")


#---Текстовые сообщения которые готовяться к отправке---
@bot.message_handler(content_types=['text'])
def Homework(message):

    global Result
    global User_level

    if(message.text != "/start" or message.text != "/info" or message.text != "/homework"):
        if(Result):

            #Подготовка к SQL запросам
            var_ID = FromDataBase_ID_LAST() + 1
            var_Task_ID = FromDataBase_Task_ID_LAST()
            var_Task_ID = var_Task_ID % 1000000 + 1
            var_ChatUser_ID = message.chat.id
            var_Answer = 0

            markup = types.InlineKeyboardMarkup()

            if(User_level == 0):
                markup.add(types.InlineKeyboardButton("Опубликовано", callback_data="HAS_ANSWER_VIP"))
                sent_message = bot.send_message(ADRES_VIP, f"🌟VIP Заданиe🌟 #⃣{var_Task_ID+3000000} \n {message.text} \n❌Не Выполнено❌", reply_markup=markup)

                var_MessageAdmin_ID = sent_message.message_id
                bot.send_message(message.chat.id, f"Отправлено, ожидайте🕐. Номер вашего задания: #⃣{var_Task_ID + 3000000}")

                ToDataBase_ALL(var_ID, var_Task_ID+3000000, var_MessageAdmin_ID, var_ChatUser_ID, var_Answer, message.date)

            if(User_level == 1):
                markup.add(types.InlineKeyboardButton("Опубликовано", callback_data="HAS_ANSWER_PREMIUM"))
                sent_message = bot.send_message(ADRES_Premium, f"⭐️Premium Заданиe⭐️ #⃣{var_Task_ID+2000000}\n {message.text} \n❌Не Выполнено❌", reply_markup=markup)

                var_MessageAdmin_ID = sent_message.message_id
                bot.send_message(message.chat.id, "Отправлено, ожидайте🕐")

                ToDataBase_ALL(var_ID, var_Task_ID+2000000, var_MessageAdmin_ID, var_ChatUser_ID, var_Answer, message.date)

            if(User_level == 2):
                markup.add(types.InlineKeyboardButton("Опубликовано", callback_data="HAS_ANSWER_BASE"))
                sent_message = bot.send_message(ADRES_Base, f"5️⃣Base Заданиe5️⃣ #⃣{var_Task_ID+1000000}\n {message.text} \n❌Не Выполнено❌", reply_markup=markup)

                var_MessageAdmin_ID = sent_message.message_id
                bot.send_message(message.chat.id, "Отправлено, ожидайте🕐")

                ToDataBase_ALL(var_ID, var_Task_ID+1000000, var_MessageAdmin_ID, var_ChatUser_ID, var_Answer, message.date)

#---Начало работы DataBase---
conn = sqlite3.connect('homework.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS tasks(
    ID INTEGER PRIMARY KEY,
    Task_ID INTEGER,
    MessageAdmin_ID INTEGER,
    ChatUser_ID INTEGER,
    Answer INTEGER,
    Time_Message INTEGER);
    ''')
conn.commit()
conn.close()

def FromDataBase_ID_LAST():
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute('''SELECT ID FROM tasks''')
    DB_CASH = cur.fetchall()
    DB_Result = DB_CASH[-1][0]

    conn.close()
    return DB_Result

def FromDataBase_Task_ID_LAST():
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute('''SELECT Task_ID FROM tasks''')
    DB_CASH = cur.fetchall()
    DB_Result = DB_CASH[-1][0]

    conn.close()
    return DB_Result

def FromDataBase_Chat_ID(var_messageAdmin_ID):
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute(f'''SELECT ChatUser_ID FROM tasks WHERE MessageAdmin_ID = {var_messageAdmin_ID}''')
    DB_CASH = cur.fetchall()
    DB_Result = DB_CASH[0][0]

    conn.close()
    return DB_Result

def FromDataBase_Task_ID(var_messageAdmin_ID):
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute(f'''SELECT Task_ID FROM tasks WHERE MessageAdmin_ID = {var_messageAdmin_ID}''')
    DB_CASH = cur.fetchall()
    DB_Result = DB_CASH[0][0]

    conn.close()
    return DB_Result

def FromDataBase_Task_ID_byTime(var_TimeMessage):
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute(f'''SELECT Task_ID FROM tasks WHERE Time_Message = {var_TimeMessage}''')
    DB_CASH = cur.fetchall()
    DB_Result = DB_CASH[0][0]

    conn.close()
    return DB_Result

def FromDataBase_MessageAdmin_ID_by_Task_ID(var_Task_ID):
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute(f'''SELECT MessageAdmin_ID FROM tasks WHERE Task_ID = {var_Task_ID}''')
    DB_CASH = cur.fetchall()
    DB_Result = DB_CASH[0][0]

    conn.close()
    return DB_Result

def ToDataBase_ALL(var_ID, var_Task_ID, var_messageAdmin_ID, var_chatUser_ID, Answer, Datatime):
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    DB_CASH = (var_ID, var_Task_ID, var_messageAdmin_ID, var_chatUser_ID, Answer, Datatime)
    cur.execute('''INSERT INTO tasks VALUES(?, ?, ?, ?, ?, ?)''', DB_CASH)
    conn.commit()

    conn.close()

def UpdateDataBase_Answer(var_messageAdmin_ID):
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute(f'''UPDATE tasks SET Answer = 1 WHERE MessageAdmin_ID = {var_messageAdmin_ID}''')
    conn.commit()

    conn.close()

def FromDataBase_Task_ID_VIP_notAnswer():
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute('''SELECT Task_ID FROM tasks WHERE Task_ID > 3000000 AND Answer = 0''')
    DB_Result = cur.fetchall()

    conn.close()
    return DB_Result

def FromDataBase_Task_ID_Premium_notAnswer():
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute('''SELECT Task_ID FROM tasks WHERE  Task_ID > 200000 AND Task_ID < 3000000 AND Answer = 0''')
    DB_Result = cur.fetchall()

    conn.close()
    return DB_Result

def FromDataBase_Task_ID_BASE_notAnswer():
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute('''SELECT Task_ID FROM tasks WHERE Task_ID > 1000000 AND Task_ID < 2000000 AND Answer = 0''')
    DB_Result = cur.fetchall()

    conn.close()
    return DB_Result

def FromDataBase_TimeMessage():
    conn = sqlite3.connect('homework.db')
    cur = conn.cursor()

    cur.execute('''SELECT Time_Message FROM tasks WHERE Task_ID > 3000000 AND Answer = 0''')
    DB_Result = cur.fetchall()

    conn.close()
    return DB_Result

bot.polling(none_stop=True)