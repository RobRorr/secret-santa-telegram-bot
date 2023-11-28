import os
import json
import telebot
import validators
import random
from setconfig import setconfig

#Set configuration
config_file_path = os.path.normpath('config.ini')
config = setconfig(config_file_path)
json_file_path = config.get('json_file_path')
telegram_token = config.get('telegram_token')
admin_id = config.get('admin')

bot = telebot.TeleBot(telegram_token)

#Standard commad
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'group':
        return
    response = "Welcome to our Secret Santa!"
    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def start(message):
    if message.chat.type == 'group':
        return
    response = "Use '/addme' to add yourself to the list of participants and follow the steps, at the right time you will receive a message with the name of your recipient and their wish list if they have one. Everyone can only add themselves. In case of errors use '/removeme' and you can redo the procedure. Every other message will be ignored, use '/start' to check that the bot is awake."
    bot.reply_to(message, response)

#Add user to list
@bot.message_handler(commands=['addme'])
def start(message):
    if message.chat.type == 'group':
        return
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            list = data['list']
            if len(list)>0:
                chat_id_list = take_chat_id_list(list)
                if message.chat.id in chat_id_list:
                    bot.reply_to(message, 'You are already on the list')
                    return
        except Exception as e:
            bot.reply_to(message, 'oooops')
    msg = bot.reply_to(message, 'Insert your name')
    bot.register_next_step_handler(msg, name_step)

#Remove user from list
@bot.message_handler(commands=['removeme'])
def start(message):
    if message.chat.type == 'group':
        return
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        data['list'] = remove_participant(data['list'], message.chat.id)
        with open(json_file_path, 'w') as f:
            json.dump(data, f)
    response = "Done!"
    bot.reply_to(message, response)

#Admin commands
@bot.message_handler(commands=['startsecretsanta'])
def start(message):
    if message.chat.id == admin_id:
        startsecretsanta(message)
        bot.reply_to(message, "Let's get started")
    else:
        bot.reply_to(message, 'You are not the admin')

@bot.message_handler(commands=['removeall'])
def start(message):
    if message.chat.id == admin_id:
        remove_all_participants(message)
    else:
        bot.reply_to(message, 'You are not the admin')

@bot.message_handler(commands=['removeparticipant'])
def start(message):
    if message.chat.id == admin_id:
        msg = bot.reply_to(message, 'Insert the id')
        bot.register_next_step_handler(msg, remove_id_step)
    else:
        bot.reply_to(message, 'You are not the admin')

#Participant management
#2nd step of /addme
def name_step(message):
    name = message.text
    msg = bot.reply_to(message, 'If you want to add the wishlist, please insert the link')
    bot.register_next_step_handler(msg, link_step, name)

#3rd step of /addme
def link_step(message, name):
    try:
        chat_id = message.chat.id
        link = message.text
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, 'r') as f:
                    data = json.load(f)
            except Exception as e:
                bot.reply_to(message, 'oooops')
        else:
            data = {}
        if 'list' in data:
            element = [chat_id, name, link]
            data['list'] = add_participant(data['list'], element)
        else:
            element = [chat_id, name, link]
            data['list'] = [element]
        with open(json_file_path, 'w') as f:
            json.dump(data, f)
        response = "Done!"
        if not validators.url(link):
            msg = bot.reply_to(message, 'You are in! (No wishlist saved)')
            return
        else:
            bot.send_message(chat_id, 'You are in!')
    except Exception as e:
        bot.reply_to(message, 'oooops')

def take_chat_id_list(list_of_triples):
    return [triple[0] for triple in list_of_triples]

def add_participant(list, element):
    list.append(element)
    return list

def remove_participant(list, element):
    list = [t for t in list if t[0] != element]
    return list

#Admin management
def remove_all_participants(message):
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        data['list'] = []
        with open(json_file_path, 'w') as f:
            json.dump(data, f)
    response = "Done!"
    bot.reply_to(message, response)

def remove_id_step(message):
    try:
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            data['list'] = remove_participant(data['list'], message.text)
            with open(json_file_path, 'w') as f:
                json.dump(data, f)
        response = "Done!"
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, 'oooops')

def startsecretsanta(message):
    try:
        if not os.path.exists(json_file_path):
            return
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        list = data['list']
        random.shuffle(list)
        for i in range(len(list)):
            recipient = list[(i + 1) % len(list)]
            if not validators.url(recipient[2]):
                bot.send_message(list[i][0], f"Your gift recipient is {recipient[1]}")
            else:
                bot.send_message(list[i][0], f"Your gift recipient is {recipient[1]} {recipient[2]}")
    except Exception as e:
        bot.reply_to(message, 'oooops')   

#Start bot
bot.polling()