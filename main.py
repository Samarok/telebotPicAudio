# -*- coding: cp1251 -*-
import requests
#from bs4 import BeautifulSoup as bs
import telebot
from telebot import types
from icrawler.builtin import GoogleImageCrawler
import os
import time
import yt_dlp
#import pafy
#from PIL import Image

URL = 'https://cbr.ru/currency_base/daily/'
API_KEY = ''

'''
headers = {
    'accept': '*/*',
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

URL - переменная содержащая ссылку на сайт, с которого берём данные о курсе валют
API_KEY - это API-ключ нашего телеграмм бота, т.е. его собственный идентификатор
'''

global path
path = 'tempPicture'

bot = telebot.TeleBot(API_KEY)
global markup
markup = types.InlineKeyboardMarkup(row_width=1)
item1 = types.InlineKeyboardButton('Поиск изображений по запросу', callback_data='menu:picture')
item2 = types.InlineKeyboardButton('Поиск аудиофайлов по запросу', callback_data='menu:audio')
item3 = types.InlineKeyboardButton('Ссылка на GitHub', callback_data='menu:git')
markup.add(item1, item2, item3)


def parser_pic(request):
    google_crawler = GoogleImageCrawler(storage={'root_dir': path})
    google_crawler.crawl(keyword=request, max_num=1)
    return 0

def parser_audio(request):
    if not os.path.exists('tempPicture'):
        os.makedirs('tempPicture')

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': ('tempPicture/' + str(request) + '.mp3'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch:{request}", download=True)
            if search_results['entries']:
                video_url = search_results['entries'][0]['url']
                ydl.download([video_url])
                audio_file = f"tempPicture/{request}.mp3"
                if os.path.exists(audio_file):
                    return audio_file
                else:
                    return None
            else:
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def gen_picture(message):
    bot.clear_step_handler_by_chat_id(message)
    #bot.send_message(message.chat.id, message.text + '111')
    if (message.text == 'Вернуться в меню' or message.text == '/start'):
        #bot.send_message(message.chat.id, message.text + '222')
        a = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Выполняю', reply_markup=a)
        bot.send_message(message.chat.id, 'Что вы хотите сделать?:', reply_markup=markup)
        #bot.clear_step_handler_by_chat_id(message)
        return 0
    else:
        parser_pic(message.text)

        while not os.path.exists('tempPicture/000001.jpg') and not os.path.exists('tempPicture/000001.png'):
            time.sleep(0.5)
        if os.path.exists('tempPicture/000001.jpg'):
            bot.send_photo(message.chat.id, photo=open('tempPicture/000001.jpg', 'rb'))
            os.remove('tempPicture/000001.jpg')
        elif os.path.exists('tempPicture/000001.png'):
            bot.send_photo(message.chat.id, photo=open('tempPicture/000001.png', 'rb'))
            os.remove('tempPicture/000001.png')

        time.sleep(0.1)
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton(text="Вернуться в меню")
        markup1.add(button1)
        bot.send_message(message.chat.id, 'Введите запрос или вернитесь в меню', reply_markup=markup1)
    #bot.clear_step_handler_by_chat_id(message)
    bot.register_next_step_handler(message, gen_picture)
    return 0


def gen_audio(message):
    bot.clear_step_handler_by_chat_id(message)
    if (message.text == 'Вернуться в меню' or message.text == '/start'):
        #bot.send_message(message.chat.id, message.text + '222')
        a = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Выполняю', reply_markup=a)
        bot.send_message(message.chat.id, 'Что вы хотите сделать?:', reply_markup=markup)
        #bot.clear_step_handler_by_chat_id(message)
        return 0
    else:
        audio_file = parser_audio(message.text)
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)
            os.remove(audio_file)  # Удаляем файл после отправки
        else:
            bot.reply_to(message.text, "Не удалось найти найти указанный аудио файл.")
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton(text="Вернуться в меню")
        markup1.add(button1)
        bot.send_message(message.chat.id, 'Введите запрос или вернитесь в меню', reply_markup=markup1)
        # bot.clear_step_handler_by_chat_id(message)
    bot.register_next_step_handler(message, gen_audio)
    return 0



@bot.message_handler(commands=['start'])
# функция, которая запускается при вводе команды 'start'
def start(message):
    bot.send_message(message.chat.id, 'Что вы хотите сделать?:', reply_markup=markup)
    bot.clear_step_handler_by_chat_id(message)
    return 0


@bot.callback_query_handler(func=lambda call: call.data.split(":")[0] == "menu")
def callback1(call):
    bot.clear_step_handler_by_chat_id(call.message)
    if call.message:
        if call.data.split(":")[1] == 'picture':
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 'Вы выбрали поиск изображений.\nВведите запрос:')
            bot.register_next_step_handler(call.message, gen_picture)
            #bot.clear_step_handler_by_chat_id(call.message)
        elif call.data.split(":")[1] == 'audio':
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 'Вы выбрали поиск аудио.\nВведите запрос:')
            bot.register_next_step_handler(call.message, gen_audio)
            #bot.clear_step_handler_by_chat_id(call.message)
        elif call.data.split(":")[1] == 'git':
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 'Ссылка на GitHub:')
            bot.send_message(call.message.chat.id, 'https://github.com/Samarok/telebotPicAudio.git')
            bot.send_message(call.message.chat.id, 'Что вы хотите сделать?:', reply_markup=markup)


    #bot.clear_step_handler_by_chat_id(call.message)
    return 0


bot.polling()

# Lab 1
# Сампилов Арсений
