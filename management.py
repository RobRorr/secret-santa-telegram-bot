import os
import json
import random
import telebot
import validators

import setconfiguration
from languages import dictionary

bot = telebot.TeleBot(setconfiguration.telegram_token)
language = setconfiguration.language


def add_participant(list, element):
    return list.append(element)

def create_list_step(message):
    listname = message.text
    if os.path.exists(setconfiguration.json_file_path):
        data = read_data(message)
        if listname in data:
            bot.reply_to(message, dictionary[language]['group_exists'])
            return
        else:
            data[listname] = []
            write_data(data)
            bot.reply_to(message, dictionary[language]['group_added'])
            return
    else:
        data = {}
        data[listname] = []
        write_data(data)
        bot.reply_to(message, dictionary[language]['group_added'])

def remove_all_participants(message):
    data = read_data(message)
    for list in data:
        data[list] = []
    write_data(data)
    bot.reply_to(message, dictionary[language]['done'])

def remove_id_step(message):
    data = read_data(message)
    for list in data:
        data[list] = remove_participant(data[list], message.text)
    write_data(data)
    bot.reply_to(message, dictionary[language]['done'])

def remove_participant(list, element):
    return [triple for triple in list if triple[0] != int(element)]

def startsecretsanta(message):
    data = read_data(message)
    for l in data:
        list = data[l]
        random.shuffle(list)
        for i in range(len(list)):
            recipient = list[(i + 1) % len(list)]
            if not validators.url(recipient[2]):
                msg = dictionary[language]['recipient'] + recipient[1]
            else:
                msg = dictionary[language]['recipient'] + recipient[1] + " : " + recipient[2]
            bot.send_message(list[i][0], msg)

def take_chat_id_list(list_of_triples):
    return [triple[0] for triple in list_of_triples]

def read_data(message):
    try:
        with open(setconfiguration.json_file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        bot.reply_to(message, dictionary[language]['error'])
    return data

def write_data(data):
    with open(setconfiguration.json_file_path, 'w') as f:
        json.dump(data, f)