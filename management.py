import json
import logging
import os

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
    couples = gift_pairs(participant_list) or {}
    for i in range(len(couples)):
        if not validators.url(couples[1][3]):
            msg = lex['recipient'] + couples[1][0]
        else:
            msg = lex['recipient'] + couples[1][0] + " : " + couples[1][1]
        bot.send_message(participant_list[i][0], msg)


def create_valid_pairs_map(participant_list):
    valid_pairs = {}
    for giver in participant_list:
        valid_pairs[tuple(giver)] = [
            receiver for receiver in participant_list
            if receiver[1] != giver[1] and receiver[1] != giver[3]
        ]
    return valid_pairs


def find_pairs(participant_list, valid_pairs, index=0, pairs=None, cache=None):
    if pairs is None:
        pairs = []
    if cache is None:
        cache = {}
    if index == len(participant_list):
        return pairs
    giver = participant_list[index]
    giver_key = tuple(giver)
    for receiver in valid_pairs[giver_key]:
        key = (giver[1], receiver[1])
        if key in cache:
            continue
        pairs.append((giver, receiver))
        cache[key] = True
        result = find_pairs(participant_list, valid_pairs, index + 1, pairs, cache)
        if result:
            return result
        pairs.pop()
        cache.pop(key, None)
    return None


def gift_pairs(participant_list):
    valid_pairs = create_valid_pairs_map(participant_list)
    sorted_participants = sorted(participant_list, key=lambda x: len(valid_pairs[tuple(x)]))
    result = find_pairs(sorted_participants, valid_pairs)
    return result


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
    return ",\n".join(participant_list)


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
