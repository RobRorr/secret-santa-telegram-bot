import json
import logging
import os
import random

import telebot
import validators

import bot_config
from languages import dictionary

bot = telebot.TeleBot(bot_config.telegram_token)
lex = dictionary[bot_config.language]


def add_participant(participant_list, element):
    return participant_list.append(element)


def create_list_step(message):
    if os.path.exists(bot_config.json_file_path):
        data = read_data(message)
        if message.text in data:
            bot.reply_to(message, lex['group_exists'])
            return
        else:
            data[message.text] = []
            write_data(message, data)
            bot.reply_to(message, lex['group_added'])
            return
    else:
        data = {message.text: []}
        write_data(message, data)
        bot.reply_to(message, lex['group_added'])


def remove_all_participants(message):
    data = read_data(message)
    for participant_list in data:
        data[participant_list] = []
    write_data(message, data)
    bot.reply_to(message, lex['done'])


def remove_id_step(message):
    data = read_data(message)
    for participant_list in data:
        data[participant_list] = remove_participant(data[participant_list], message.text)
    write_data(message, data)
    bot.reply_to(message, lex['done'])


def remove_participant(participant_list, element):
    return [quartet for quartet in participant_list if quartet[0] != int(element)]


def secret_santa(message):
    data = read_data(message)
    if message.text in data:
        start_secret_santa(data[message.text])
    else:
        bot.reply_to(message, lex['group_no_exists'])


def secret_santa_all(message):
    data = read_data(message)
    for l in data:
        start_secret_santa(data[l])


def start_secret_santa(participant_list):
    couples = gift_couples(participant_list) or {}
    for i in range(len(couples)):
        if not validators.url(couples[1][3]):
            msg = lex['recipient'] + couples[1][0]
        else:
            msg = lex['recipient'] + couples[1][0] + " : " + couples[1][1]
        bot.send_message(participant_list[i][0], msg)


def gift_couples(participant_list):
    for attempt in range(len(participant_list) ^ 2):
        recipient_list = random.sample(participant_list, len(participant_list))
        valid = True

        for i in range(len(participant_list)):
            if participant_list[i][3] == recipient_list[i][1] or participant_list[i][1] == recipient_list[i][1]:
                valid = False
                break

        if valid:
            return [list[participant_list[i], recipient_list[i]] for i in range(len(participant_list))]


def get_participant_list(group_name):
    data = read_data(group_name)
    participant_list = []
    if group_name in data:
        group = data[group_name]
        for i in range(len(group)):
            participant_list.append(group[i][1])
    return ",\n".join(participant_list)


def take_chat_id_list(list_of_triples):
    return [triple[0] for triple in list_of_triples]


def read_data(message):
    try:
        with open(bot_config.json_file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        bot.reply_to(message, lex['error'])
        logging.debug(e)
    return data


def write_data(message, data):
    try:
        with open(bot_config.json_file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        bot.reply_to(message, lex['error'])
        logging.debug(e)
