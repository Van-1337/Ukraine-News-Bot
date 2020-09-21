#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import const
import datetime
from threading import Thread
import logging
from time import sleep
from os import abort
import sqlite3
import parse
from parse import Update
from keyboards import commandkeyboard, infokeyboard, settingskeyboard, firsttimekeyboard, secondtimekeyboard

logging.basicConfig(filename="mailing.log", level=logging.INFO)  # Не работает кста, заполняет в файл Parse.log
log = logging.getLogger("ex")
logging.info("START WORKING!")

print("Подключаемся к базе...")
try:
    conn = sqlite3.connect('Mail_bot', check_same_thread=False)  # Tables: first_mail, second_mail
    print("Подключение прошло успешно!")
    conn.execute(
        "create table if not exists first_mail (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, time INTEGER,"
        "Course BOOLEAN NOT NULL CHECK (Course IN (0,1)),Corona BOOLEAN NOT NULL CHECK (Corona IN (0,1)),"
        "Weather BOOLEAN NOT NULL CHECK (Weather IN (0,1)),Holiday BOOLEAN NOT NULL CHECK (Holiday IN (0,1)),"
        "Shares BOOLEAN NOT NULL CHECK (Shares IN (0,1)), NewsWithAPI BOOLEAN NOT NULL CHECK (NewsWithAPI IN (0,1)),"
        "CityNews BOOLEAN NOT NULL CHECK (CityNews IN (0,1)),NewsYandex BOOLEAN NOT NULL CHECK (NewsYandex IN (0,1)),"
        "GTopNews BOOLEAN NOT NULL CHECK (GTopNews IN (0,1)),GWorldNews BOOLEAN NOT NULL CHECK (GWorldNews IN (0,1)),"
        "GUkrainianNews BOOLEAN NOT NULL CHECK (GUkrainianNews IN (0,1)),"
        "GTechnologyNews BOOLEAN NOT NULL CHECK (GTechnologyNews IN (0,1)),"
        "GScienceNews BOOLEAN NOT NULL CHECK (GScienceNews IN (0,1)),"
        "GSportsNews BOOLEAN NOT NULL CHECK (GSportsNews IN (0,1)))")
    conn.execute(
        "create table if not exists second_mail (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, time INTEGER,"
        "Course BOOLEAN NOT NULL CHECK (Course IN (0,1)),Corona BOOLEAN NOT NULL CHECK (Corona IN (0,1)),"
        "Weather BOOLEAN NOT NULL CHECK (Weather IN (0,1)),Holiday BOOLEAN NOT NULL CHECK (Holiday IN (0,1)),"
        "Shares BOOLEAN NOT NULL CHECK (Shares IN (0,1)), NewsWithAPI BOOLEAN NOT NULL CHECK (NewsWithAPI IN (0,1)),"
        "CityNews BOOLEAN NOT NULL CHECK (CityNews IN (0,1)),NewsYandex BOOLEAN NOT NULL CHECK (NewsYandex IN (0,1)),"
        "GTopNews BOOLEAN NOT NULL CHECK (GTopNews IN (0,1)),GWorldNews BOOLEAN NOT NULL CHECK (GWorldNews IN (0,1)),"
        "GUkrainianNews BOOLEAN NOT NULL CHECK (GUkrainianNews IN (0,1)),"
        "GTechnologyNews BOOLEAN NOT NULL CHECK (GTechnologyNews IN (0,1)),"
        "GScienceNews BOOLEAN NOT NULL CHECK (GScienceNews IN (0,1)),"
        "GSportsNews BOOLEAN NOT NULL CHECK (GSportsNews IN (0,1)))")
    conn.commit()
except:
    log.exception("Ошибка подключения к базе данных")

bot = telebot.TeleBot(const.TelegramToken)


def test_send_message_with_markdown(self):
    markdown = """
    *bold text*
    _italic text_
    [text](URL)
    """
    ret_msg = tb.send_message(CHAT_ID, markdown, parse_mode="Markdown")
    assert ret_msg.message_id


def Statistics(): # возвращает количество пользователей
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM first_mail')
    Amount = len(list(cursor))
    cursor.close()
    return str(Amount)

on=1
def Mailing():  # Работает в отельном потоке, рассылает и парсит информацию в нужное время
    print("Идёт обновление информации...")
    logging.info("Update info...")
    Update()
    logging.info("Update successful!")
    print ("Информация обновлена!")
    while on:
        time = datetime.datetime.now() + datetime.timedelta(hours=const.deltahours)
        if 60-time.minute-const.timetoprepare > 0:  # Если нужно ждать
            logging.info("Wait " + str(60-time.minute-const.timetoprepare) + " minutes")
            sleep((60-time.minute-const.timetoprepare)*60)  # Ждёт до момента подготовки
        logging.info("Update info...")
        Update()
        logging.info("Update successful!")
        while datetime.datetime.now().minute > 1:  # пока не наступил момент рассылки, ждём 2 сек и проверяем снова
            sleep(2)
        cursor = conn.cursor()
        hoursnow = datetime.datetime.now().hour+const.deltahours  # который сейчас час (нужно чтобы понять кому сейчас рассылать информацию)
        logging.info("Get user info to mail")
        if hoursnow <= 12:
            cursor.execute('SELECT * FROM first_mail')
        else:
            cursor.execute('SELECT * FROM second_mail')
        hoursnow *= 60
        logging.info("Begin mailing!")
        for row in cursor:  # row - информация об отдельном пользователе
            if row[1] == hoursnow:
                if row[2] == 1:  # если столбец Course в БД равен 1, то отослать курс
                    try:
                        bot.send_message(row[0], parse.course, parse_mode='HTML')
                    except:  # Если сообщение не прошло, то пользователь просто отключил бота, не стоит подымать панику
                        continue
                if row[4] == 1:
                    try:
                        bot.send_message(row[0], parse.weather, parse_mode='HTML')
                    except:
                        continue
                if row[7] == 1:
                    try:
                        bot.send_message(row[0], parse.newswithapi, parse_mode='HTML')
                    except:
                        pass  # тут pass а continue, потому что при парсинге новостей могла произойти ошибка, тогда лучше просто пропустить
                #if (row[9]==1):
                #    try:
                #        bot.send_message(row[0], parse.newsyandex, parse_mode='HTML')
                #    except:
                #        pass
                if row[3] == 1:
                    try:
                        bot.send_message(row[0], parse.corona, parse_mode='HTML')
                    except:
                        pass
                if row[5] == 1:
                    try:
                        bot.send_message(row[0], parse.holiday, parse_mode='HTML')
                    except:
                        pass
                if row[6] == 1:
                    try:
                        bot.send_message(row[0], parse.shares, parse_mode='HTML')
                    except:
                        pass
                if  row[8] == 1:
                    try:
                        bot.send_message(row[0], parse.kharkivnews, parse_mode='HTML')
                    except:
                        pass
                if row[10] == 1:
                    try:
                        bot.send_message(row[0], parse.Gtopnews, parse_mode='HTML')
                    except:
                        pass
                if row[11] == 1:
                    try:
                        bot.send_message(row[0], parse.Gworldnews, parse_mode='HTML')
                    except:
                        pass
                if row[12] == 1:
                    try:
                        bot.send_message(row[0], parse.Gukrainiannews, parse_mode='HTML')
                    except:
                        pass
                if row[13] == 1:
                    try:
                        bot.send_message(row[0], parse.Gtechnologynews, parse_mode='HTML')
                    except:
                        pass
                if row[14] == 1:
                    try:
                        bot.send_message(row[0], parse.Gsciencenews, parse_mode='HTML')
                    except:
                        pass
                if row[15] == 1:
                    try:
                        bot.send_message(row[0], parse.Gsportsnews, parse_mode='HTML')
                    except:
                        pass
        logging.info("mailing end")
        cursor.close()
    logging.info("End work")  # Срабатывает когда поток закончен (т.е. когда нажато Ctrl+C)
    print ("Работа завершена!")


def CheckUser(user):  # проверяет наличие пользователя в БД, если его там нет, то добавляет
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM first_mail WHERE id = ' + str(user))
        if (len(list(cursor)) == 0):
            cursor.execute("insert into " + "first_mail (id, time, Course, Corona, Weather, Holiday, Shares, NewsWithAPI, CityNews, NewsYandex, GTopNews, GWorldNews, GUkrainianNews, GTechnologyNews, GScienceNews, GSportsNews) values (" + str(user) + ",  420, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0);")
            conn.commit()
        cursor.execute('SELECT * FROM second_mail WHERE id = ' + str(user))
        if (len(list(cursor)) == 0):
            cursor.execute("insert into " + "second_mail (id, time, Course, Corona, Weather, Holiday, Shares, NewsWithAPI, CityNews, NewsYandex, GTopNews, GWorldNews, GUkrainianNews, GTechnologyNews, GScienceNews, GSportsNews) values (" + str(user) + ", 1200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);")
            conn.commit()
    except Exception as e:
        log.exception("Error20 ", e)


@bot.message_handler(commands=['start'])
def start(message):
    try:
        global conn
        user = message.chat.id
        bot.send_message(user, "Привет! Этот бот будет рассылать всю актуальную информацию в указанное время.\n"
                               "⚙Настройки - уточнить время рассылки и рассылаемую информацию\n"
                               "✍Последние рассылки - просмотреть последнюю рассылку", reply_markup=commandkeyboard)
        CheckUser(user)
    except:
        log.exception("Error21")


@bot.message_handler(content_types=['text'])
def main(message):
    text = message.text
    user = message.chat.id
    try:
        if text == '✍Последние рассылки':
            bot.send_message(user, "Выберите пункт для просмотра последней рассылки", parse_mode="Markdown",
                             reply_markup=infokeyboard)
            bot.register_next_step_handler(message, last_mail)
        elif text == '⚙Настройки':
            CheckUser(user)
            bot.send_message(user, "Первая рассылка до 12 часов, вторая - после 12. Выберите рассылку для настройки:",
                             parse_mode="Markdown", reply_markup=settingskeyboard)
        elif text == '/statistics':
            bot.send_message(user, "В моей базе данных " + Statistics() + " пользователей")
        else:
            CheckUser(user)
            bot.send_message(user, "Я вас не понимаю(", parse_mode="Markdown", reply_markup=commandkeyboard)
    except:
        try:
            bot.send_message(user, "Ошибка22", reply_markup=commandkeyboard)
        except:
            pass
        log.exception("Error22")


def last_mail(message):  # меню выбора последней рассылки
    text = message.text
    user = message.chat.id
    if text == 'Курсы валют':
        try:
            bot.send_message(user, parse.course, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка30")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error30")
    elif text == 'Погода':
        try:
            bot.send_message(user, parse.weather, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка31")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error31")
    elif text == 'Ещё одни новости':
        try:
            bot.send_message(user, parse.newswithapi, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка32")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error32")
    elif text == 'Новости Яндекса':
        try:
            bot.send_message(user, parse.newsyandex, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка33")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error33")
    elif text == 'КоРоНаВиРуС':
        try:
            bot.send_message(user, parse.corona, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка34")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error34")
    elif text == 'Праздник':
        try:
            bot.send_message(user, parse.holiday, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка35")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error35")
    elif text == 'Акции':
        try:
            bot.send_message(user, parse.shares, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка36")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error36")
    elif text == 'Харьк. новости':
        try:
            bot.send_message(user, parse.kharkivnews, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка37")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error37")
    elif text == 'Главные новости':
        try:
            bot.send_message(user, parse.Gtopnews, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка38")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error38")
    elif text == 'Мировые новости':
        try:
            bot.send_message(user, parse.Gworldnews, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка39")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error39")
    elif text == 'Украинские новости':
        try:
            bot.send_message(user, parse.Gukrainiannews, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка310")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error310")
    elif text == 'Новости технологий':
        try:
            bot.send_message(user, parse.Gtechnologynews, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка311")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error311")
    elif text == 'Новости науки':
        try:
            bot.send_message(user, parse.Gsciencenews, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка312")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error312")
    elif text == 'Новости спорта':
        try:
            bot.send_message(user, parse.Gsportsnews, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка313")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error313")
    elif text == 'Источники':
        try:
            bot.send_message(user, const.sources, parse_mode='HTML')
            bot.register_next_step_handler(message, last_mail)
        except:
            try:
                bot.send_message(user, "Ошибка333")
                bot.register_next_step_handler(message, last_mail)
            except:
                pass
            log.exception("Error333")
    else:
        bot.send_message(user, "Выходим в главное меню", reply_markup=commandkeyboard)


switch = {0: "❌", 1: "✅"}  # 0-пункт не включен, 1 - включен
def GenerateKeyboard (Table, info):  # генерирует клавиатуру выбора расссылки
    reskeyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    if Table == "first_mail":
        time = "FirstTime"
    else:
        time = "SecondTime"
    if info[1] == -1:
        item0 = telebot.types.InlineKeyboardButton("ВЫКЛ", callback_data=time)
    else:
        item0 = telebot.types.InlineKeyboardButton("Время " + str(info[1]//60) + ":00", callback_data=time)
    # First_mail Course - из какой таблицы что поменять с помощью запроса SET Course = ABS(Course-1)
    item1 = telebot.types.InlineKeyboardButton("Главные новости " + switch[info[10]], callback_data=Table + ' GTopNews')
    item2 = telebot.types.InlineKeyboardButton("Мировые новости " + switch[info[11]], callback_data=Table + ' GWorldNews')
    item3 = telebot.types.InlineKeyboardButton("Украинские новости " + switch[info[12]], callback_data=Table + ' GUkrainianNews')
    item4 = telebot.types.InlineKeyboardButton("Новости технологий " + switch[info[13]], callback_data=Table + ' GTechnologyNews')
    item5 = telebot.types.InlineKeyboardButton("Новости науки " + switch[info[14]], callback_data=Table + ' GScienceNews')
    item6 = telebot.types.InlineKeyboardButton("Новости спорта " + switch[info[15]], callback_data=Table + ' GSportsNews')
    item7 = telebot.types.InlineKeyboardButton("Курс " + switch[info[2]], callback_data=Table + ' Course')
    item8 = telebot.types.InlineKeyboardButton("Коронавирус " + switch[info[3]], callback_data=Table + ' Corona')
    item9 = telebot.types.InlineKeyboardButton("Погода " + switch[info[4]], callback_data=Table + ' Weather')
    item10 = telebot.types.InlineKeyboardButton("Праздники " + switch[info[5]], callback_data=Table + ' Holiday')
    item11 = telebot.types.InlineKeyboardButton("Акции " + switch[info[6]], callback_data=Table + ' Shares')
    #telebot.types.InlineKeyboardButton("Новости Яндекса " + switch[info[9]], callback_data=Table + ' NewsYandex')
    item12 = telebot.types.InlineKeyboardButton("Ещё одни новости " + switch[info[7]], callback_data=Table + ' NewsWithAPI')
    item13 = telebot.types.InlineKeyboardButton("Городские новости " + switch[info[8]], callback_data=Table + ' CityNews')
    item14 = telebot.types.InlineKeyboardButton("Назад", callback_data="Back") #В меню какой рассылки нужно выйти
    reskeyboard.add(item0, item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13, item14)
    return reskeyboard

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        user = call.message.chat.id
        if call.data == "first_mail":  # настройка первой рассылки
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM first_mail WHERE id='+str(user))
                bot.edit_message_text(chat_id=user, message_id=call.message.message_id,
                                      text="Первая рассылка до 12 часов, вторая - после 12\n"
                                           "Настройки *первой* рассылки (нажмите для изменения)\n"
                                           "Чтобы отключить эту рассылку, зайдите в настройки времени",
                                      parse_mode="Markdown", reply_markup=GenerateKeyboard("first_mail", list(cursor)[0]))
            except:
                log.exception("Error40")
        elif call.data == "second_mail":  # настройка второй рассылки
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM second_mail WHERE id='+str(user))
                bot.edit_message_text(chat_id=user, message_id=call.message.message_id,
                                      text="Первая рассылка до 12 часов, вторая - после 12\n"
                                           "Настройки *второй* рассылки (нажмите для изменения)\n"
                                           "Чтобы отключить эту рассылку, зайдите в настройки времени",
                                      parse_mode="Markdown", reply_markup=GenerateKeyboard("second_mail", list(cursor)[0]))
            except:
                log.exception("Error41")
        elif call.data == "Back":  # вернуться в меню выбора рассылок
            try:
                bot.edit_message_text(chat_id=user, message_id=call.message.message_id,
                                      text="Первая рассылка до 12 часов, вторая - после 12."
                                           "Выберите рассылку для настройки:",
                                      parse_mode="Markdown", reply_markup=settingskeyboard)
            except:
                log.exception("Error42")
        elif call.data == "FirstTime":  # Выбор времени для первой рассылки
            try:
                bot.edit_message_text(chat_id=user,
                                      message_id=call.message.message_id,
                                      text="В какое время должна приходить рассылка?\n"
                                           "Чтобы выбрать время после 12, зайдите во вторую рассылку",
                                      parse_mode="Markdown", reply_markup=firsttimekeyboard)
            except:
                log.exception("Error43")
        elif call.data == "SecondTime":  # Выбор времени для второй рассылки
            try:
                bot.edit_message_text(chat_id=user, message_id=call.message.message_id,
                                      text="В какое время должна приходить рассылка?\n"
                                           "Чтобы выбрать время после 12, зайдите во вторую рассылку",
                                      parse_mode="Markdown", reply_markup=secondtimekeyboard)
            except:
                log.exception("Error44")
        elif ":" in call.data:  # если это время для рассылки... (в формате 13:00 или first:off для отключения первой рассылки)
            try:
                time = call.data.split(":")
                if len(time) == 2:
                    cursor = conn.cursor()
                    if time[1] == "off":
                        table = time[0] + "_mail"
                        cursor.execute("update " + table + " set time=-1 where id=" + str(user))
                        if table == 'first_mail':
                            number = "первой"
                        else:
                            number = "второй"
                    else:
                        time = [int(item) for item in time]
                        if time[0] <= 12:
                            table = "first_mail"
                            number = "первой"
                        else:
                            table = "second_mail"
                            number = "второй"
                        cursor.execute("update " + table + " set time="
                                       + str(time[0] * 60 + time[1]) + " where id=" + str(user))  # в БД время рассылки хранится в минутах
                    conn.commit()
                    cursor.execute('SELECT * FROM ' + table + ' WHERE id=' + str(user))
                    bot.edit_message_text(chat_id=user, message_id=call.message.message_id,
                                          text="Первая рассылка до 12 часов, вторая - после 12\n"
                                               "Настройки *" + number + "* рассылки (нажмите для изменения)\n"
                                               "Чтобы отключить эту рассылку, зайдите в настройки времени",
                                          parse_mode="Markdown", reply_markup=GenerateKeyboard(table, list(cursor)[0]))
                    cursor.close()
            except:
                log.exception("Error45")
        elif len(call.data.split()) == 2: #First_mail Course - из какой таблицы что поменять с помощью запроса SET Course = ABS(Course-1)
            try:
                change=call.data.split()
                cursor = conn.cursor()
                cursor.execute("UPDATE " + change[0] + " SET " + change[1] +
                               " = ABS(" + change[1] + " - 1) WHERE id = " + str(user)) #switch bool
                conn.commit()
                cursor.execute('SELECT * FROM ' + change[0] + ' WHERE id=' + str(user))
                if change[0] == "first_mail":
                    number = "первой"
                else:
                    number = "второй"
                bot.edit_message_text(chat_id=user, message_id=call.message.message_id,
                                      text="Первая рассылка до 12 часов, вторая - после 12\n"
                                           "Настройки *" + number + "* рассылки (нажмите для изменения)\n"
                                           "Чтобы отключить эту рассылку, зайдите в настройки времени",
                                      parse_mode="Markdown", reply_markup=GenerateKeyboard(change[0], list(cursor)[0]))
                cursor.close()
            except:
                log.exception("Error46")


MailingThread = Thread(target=Mailing)
if __name__ == '__main__':
    MailingThread.start()
    while True:
        try:
            bot.infinity_polling(True)
        except KeyboardInterrupt:
            on = 0
            print("Выходим из программы")
            log.info("End program!")
            abort()
        except:
            log.info("No access to telegram")
            print("No access to telegram")
            sleep(15)
