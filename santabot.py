import telebot
import validators

import bot_config
import management
from languages import dictionary

bot = telebot.TeleBot(bot_config.telegram_token)
lex = dictionary[bot_config.language]


# Standard command
@bot.message_handler(commands=[lex['command_start']])
def start(message):
    if not message.chat.type == 'group':
        bot.reply_to(message, lex['welcome'])


@bot.message_handler(commands=[lex['command_help']])
def start(message):
    if not message.chat.type == 'group':
        bot.reply_to(message, lex['help_response'])


# Add user to group
@bot.message_handler(commands=[lex['command_add_me']])
def start(message):
    if not message.chat.type == 'group':
        msg = bot.reply_to(message, lex['group_name_entry'])
        bot.register_next_step_handler(msg, group_name_step)


# 2nd step of /addme
def group_name_step(message):
    data = management.read_data(message)
    if message.text in data:
        if len(message.text) > 0:
            chat_id_list = management.take_chat_id_list(data[message.text])
            if message.chat.id in chat_id_list:
                bot.reply_to(message, lex['already_in'])
                return
        msg = bot.reply_to(message, lex['name_entry'])
        bot.register_next_step_handler(msg, name_user_step, message.text)
    else:
        bot.reply_to(message, lex['group_no_exists'])


# 3rd step of /addme
def name_user_step(message, participant_list):
    msg = bot.reply_to(message, lex['wish_list'])
    bot.register_next_step_handler(msg, link_step, participant_list, message.text)


# 4th step of /addme
def link_step(message, participant_list, username):
    data = management.read_data(message)
    element = [message.chat.id, username, message.text]
    data[participant_list].append(element)
    management.write_data(message, data)
    if not validators.url(message.text):
        bot.reply_to(message, lex['confirmation_no_list'])
    else:
        bot.reply_to(message, lex['confirmation_list'])


# Remove user from all lists
@bot.message_handler(commands=[lex['command_remove_me']])
def start(message):
    if not message.chat.type == 'group':
        data = management.read_data(message)
        for participant_list in data:
            data[participant_list] = management.remove_participant(data[participant_list], message.chat.id)
        management.write_data(message, data)
        bot.reply_to(message, lex['done'])


##Admin commands
# Create list
@bot.message_handler(commands=[lex['command_create_group']])
def start(message):
    if message.chat.id == bot_config.admin_id:
        msg = bot.reply_to(message, lex['group_name_entry'])
        bot.register_next_step_handler(msg, management.create_list_step)
    else:
        bot.reply_to(message, lex['admin_negative_response'])


# Start secret santa
@bot.message_handler(commands=[lex['command_secret_santa']])
def start_single_group(message):
    if message.chat.id == bot_config.admin_id:
        msg = bot.reply_to(message, lex['group_name_entry'])
        bot.register_next_step_handler(msg, management.secret_santa)
    else:
        bot.reply_to(message, lex['admin_negative_response'])


# Start secret santa
@bot.message_handler(commands=[lex['command_secret_santa_all']])
def start(message):
    if message.chat.id == bot_config.admin_id:
        management.secret_santa_all(message)
        bot.reply_to(message, lex['secret_santa'])
    else:
        bot.reply_to(message, lex['admin_negative_response'])


# Remove all participants from all lists
@bot.message_handler(commands=[lex['command_remove_all']])
def start(message):
    if message.chat.id == bot_config.admin_id:
        management.remove_all_participants(message)
    else:
        bot.reply_to(message, lex['admin_negative_response'])


# Remove participant from all lists
@bot.message_handler(commands=[lex['command_remove_participant']])
def start(message):
    if message.chat.id == bot_config.admin_id:
        msg = bot.reply_to(message, lex['id_entry'])
        bot.register_next_step_handler(msg, management.remove_id_step)
    else:
        bot.reply_to(message, lex['admin_negative_response'])


# Check admin
@bot.message_handler(commands=[lex['command_check_admin']])
def start(message):
    if message.chat.id == bot_config.admin_id:
        bot.reply_to(message, lex['admin_positive_response'])
    else:
        bot.reply_to(message, lex['admin_negative_response'])


# Start bot
bot.polling()
