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
        msg = bot.reply_to(message, lex['group_entry'])
        bot.register_next_step_handler(msg, group_name_step)


# 2nd step of /addme
def group_name_step(message):
    data = management.read_data(message)
    if message.text in data:
        if len(message.text) > 0:
            chat_id_list = management.take_chat_id_list(data[message.text])
            if message.chat.id in chat_id_list:
                bot.reply_to(message, lex['user_already_in'])
                return
        msg = bot.reply_to(message, lex['username_entry'])
        bot.register_next_step_handler(msg, name_user_step, message.text)
    else:
        bot.reply_to(message, lex['group_no_exists'])


# 3rd step of /addme
def name_user_step(message, group_name):
    participant_list = management.get_participant_list(group_name) or lex['no_participants']
    msg = bot.reply_to(message, participant_list + "\n" + lex['exclusion_user'])
    bot.register_next_step_handler(msg, exclusion_user_step, group_name, message.text)


# 4th step of /addme
def exclusion_user_step(message, group_name, username):
    msg = bot.reply_to(message, lex['wish_list'])
    bot.register_next_step_handler(msg, link_step, group_name, username, message.text)


# 5th step of /addme
def link_step(message, group_name, username, exclusion_recipient):
    data = management.read_data(message)
    element = [message.chat.id, username, exclusion_recipient, message.text]
    data[group_name].append(element)
    management.write_data(message, data)
    if not validators.url(message.text):
        bot.reply_to(message, lex['confirmation_no_list'])
    else:
        bot.reply_to(message, lex['confirmation_list'])


# Get group participant list
@bot.message_handler(commands=[lex['command_group_participant_list']])
def start(message):
    if not message.chat.type == 'group':
        msg = bot.reply_to(message, lex['group_entry'])
        bot.register_next_step_handler(msg, get_participant)


def get_participant(message):
    participant_list = management.get_participant_list(message.text) or lex['no_participants']
    bot.reply_to(message, participant_list)


# Set exclusion recipient
@bot.message_handler(commands=[lex['command_exclusion']])
def start(message):
    if not message.chat.type == 'group':
        msg = bot.reply_to(message, lex['group_entry'])
        bot.register_next_step_handler(msg, get_group_step)


def get_group_step(message):
    data = management.read_data(message)
    if message.text not in data:
        bot.reply_to(message, lex['group_no_exists'])
    else:
        msg = bot.reply_to(message, lex['recipient_entry'])
        bot.register_next_step_handler(msg, set_exclusion_step, message.text)


def set_exclusion_step(message, group_name):
    data = management.read_data(message)
    element = management.get_participant(group_name, message.chat.id)
    if element is not None:
        new_element = [element[0], element[1], message.text, element[3]]
        data[group_name] = management.remove_participant(data[group_name], message.chat.id)
        data[group_name].append(new_element)
        management.write_data(message, data)
        bot.reply_to(message, lex['done'])
    else:
        bot.reply_to(message, lex['user_not_in'])


# Remove user from all lists
@bot.message_handler(commands=[lex['command_remove_me']])
def start(message):
    if not message.chat.type == 'group':
        data = management.read_data(message)
        for group_name in data:
            data[group_name] = management.remove_participant(data[group_name], message.chat.id)
        management.write_data(message, data)
        bot.reply_to(message, lex['done'])


##Admin commands
# Create list
@bot.message_handler(commands=[lex['command_create_group']])
def start(message):
    if message.chat.id == bot_config.admin_id:
        msg = bot.reply_to(message, lex['group_entry'])
        bot.register_next_step_handler(msg, management.create_group)
    else:
        bot.reply_to(message, lex['admin_negative_response'])


# Start secret santa
@bot.message_handler(commands=[lex['command_secret_santa']])
def start_single_group(message):
    if message.chat.id == bot_config.admin_id:
        msg = bot.reply_to(message, lex['group_entry'])
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
