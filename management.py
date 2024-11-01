import json
import logging
import os
import random

import telebot
import validators

import bot_config
from languages import dictionary

bot = telebot.TeleBot(bot_config.telegram_token)
language = bot_config.language


def add_participant(participant_list, element):
    return participant_list.append(element)


def create_list_step(message):
    if os.path.exists(bot_config.json_file_path):
        data = read_data(message)
        if message.text in data:
            bot.reply_to(message, dictionary[language]['group_exists'])
            return
        else:
            data[message.text] = []
            write_data(message, data)
            bot.reply_to(message, dictionary[language]['group_added'])
            return
    else:
        data = {message.text: []}
        write_data(message, data)
        bot.reply_to(message, dictionary[language]['group_added'])


def remove_all_participants(message):
    data = read_data(message)
    for participant_list in data:
        data[participant_list] = []
    write_data(message, data)
    bot.reply_to(message, dictionary[language]['done'])


def remove_id_step(message):
    data = read_data(message)
    for participant_list in data:
        data[participant_list] = remove_participant(data[participant_list], message.text)
    write_data(message, data)
    bot.reply_to(message, dictionary[language]['done'])


def remove_participant(participant_list, element):
    return [triple for triple in participant_list if triple[0] != int(element)]


def secret_santa(message):
    data = read_data(message)
    if message.text in data:
        start_secret_santa(data[message.text])
    else:
        bot.reply_to(message, dictionary[language]['group_no_exists'])


def secret_santa_all(message):
    data = read_data(message)
    for l in data:
        start_secret_santa(data[l])


def start_secret_santa(participant_list):
    random.shuffle(participant_list)
    for i in range(len(participant_list)):
        recipient = participant_list[(i + 1) % len(participant_list)]
        if not validators.url(recipient[2]):
            msg = dictionary[language]['recipient'] + recipient[1]
        else:
            msg = dictionary[language]['recipient'] + recipient[1] + " : " + recipient[2]
        bot.send_message(participant_list[i][0], msg)


def take_chat_id_list(list_of_triples):
    return [triple[0] for triple in list_of_triples]


def read_data(message):
    try:
        with open(bot_config.json_file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        bot.reply_to(message, dictionary[language]['error'])
        logging.debug(e)
    return data


def write_data(message, data):
    try:
        with open(bot_config.json_file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        bot.reply_to(message, dictionary[language]['error'])
        logging.debug(e)
