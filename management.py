import json
import logging
import os
from random import shuffle

import telebot
import validators

import bot_config
from languages import dictionary

bot = telebot.TeleBot(bot_config.telegram_token)
lex = dictionary[bot_config.language]


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


def create_valid_pairs_map(participant_list):
    valid_pairs = {}
    shuffle(participant_list)
    for giver in participant_list:
        giver_key = tuple(giver)
        valid_pairs[giver_key] = [
            receiver for receiver in participant_list
            if receiver[1] != giver[1] and receiver[1] != giver[2]
        ]
    return valid_pairs


def find_pairs(participant_list, valid_pairs, index=0, pairs=None, used_receivers=None):
    if pairs is None:
        pairs = []
    if used_receivers is None:
        used_receivers = set()
    if index == len(participant_list):
        return pairs
    giver = participant_list[index]
    giver_key = tuple(giver)
    for receiver in valid_pairs.get(giver_key, []):
        if receiver[1] in used_receivers:
            continue
        pairs.append((giver, receiver))
        used_receivers.add(receiver[1])
        result = find_pairs(participant_list, valid_pairs, index + 1, pairs, used_receivers)
        if result:
            return result
        pairs.pop()
        used_receivers.remove(receiver[1])
    return None


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


def gift_pairs(participant_list):
    valid_pairs = create_valid_pairs_map(participant_list)
    sorted_participants = sorted(participant_list, key=lambda x: len(valid_pairs[tuple(x)]))
    result = find_pairs(sorted_participants, valid_pairs)
    return result


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
    couples = gift_pairs(group_name) or []
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
