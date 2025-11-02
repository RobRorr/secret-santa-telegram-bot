import json
import logging
import os
import random

import telebot

import bot_config
from languages import dictionary

max_retry = bot_config.max_retry
lex = dictionary[bot_config.language]
bot = telebot.TeleBot(bot_config.telegram_token)


def create_group(message):
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


def get_participant(group_name, username):
    data = read_data(group_name)
    if group_name in data:
        group = data[group_name]
        for i in range(len(group)):
            if group[i][0] == username:
                return group[i]
    return None


def get_participant_list(group_name):
    data = read_data(group_name)
    participant_list = []
    if group_name in data:
        group = data[group_name]
        for i in range(len(group)):
            participant_list.append(group[i][1])
    if participant_list:
        return lex['participant_list_header'] + ",\n".join(participant_list)
    else:
        return None


def create_gift_pairs(participants):
    for _ in range(max_retry):
        random.shuffle(participants)
        givers = participants[:]
        receivers = participants[:]
        pairs = []
        valid = True
        for giver in givers:
            found = False
            excluded_receivers = [excluded_receiver.strip()
                                  for excluded_receiver in giver[2].split('|')
                                  if excluded_receiver.strip()]
            while receivers and not found:
                receiver = random.choice(receivers)
                if giver == receiver or receiver[1] in excluded_receivers:
                    continue
                pairs.append((giver, receiver))
                receivers.remove(receiver)
                found = True
            if not found:
                valid = False
                break
        if valid and len(pairs) == len(participants):
            return pairs
    return None


def remove_all_participants(message):
    data = read_data(message)
    for group_name in data:
        data[group_name] = []
    write_data(message, data)
    bot.reply_to(message, lex['done'])


def remove_id_step(message):
    data = read_data(message)
    for group_name in data:
        data[group_name] = remove_participant(data[group_name], message.text)
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
    for group_name in data:
        start_secret_santa(data[group_name])


def start_secret_santa(group_name):
    couples = create_gift_pairs(group_name) or []
    if len(couples) == 0:
        logging.debug("No valid couples found")
    else:
        for i in range(len(couples)):
            giver, recipient = couples[i]
            if not validators.url(recipient[3]):
                msg = lex['recipient'] + recipient[1]
            else:
                msg = lex['recipient'] + recipient[1] + " : " + recipient[3]
            bot.send_message(giver[0], msg)


def take_chat_id_list(list_of_triples):
    return [triple[0] for triple in list_of_triples]


def read_data(message):
    try:
        with open(bot_config.json_file_path, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        bot.reply_to(message, lex['error'])
        logging.debug(e)


def write_data(message, data):
    try:
        with open(bot_config.json_file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        bot.reply_to(message, lex['error'])
        logging.debug(e)
