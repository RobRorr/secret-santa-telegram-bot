# secret-santa-telegram-bot
A simple Telegram bot that manages the Secret Santa. 

# Usage
The admin creates the group.
Each participant must add themselves to the list using the private Telegram chat with the bot. 
It uses chat IDs and a json file to reconize and manage the participants.

# Configuration
Modify the config.ini file before starting.
```
JSON_FILE_PATH = your_json_file_path
TELEGRAM_TOKEN = your_telegram_token
ADMIN = your_chat_id
LANGUAGE = your_language
```
If you need to know how to start a bot, you can find the information at [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).

# Commands

###### All Users

`/start`  
Send a personal message

`/help`  
Describe usage

`/addme`  
Add user to secret santa group

`/removeme`  
Remove user from all secret santa groups

###### Admin
`/creategroup`  
Create a new secret santa group

`/startsecretsanta`  
Send messagge to all participants of all groups with recipient's name and wishlist

`/removeall`  
Clear all the secret santa groups

`/removeparticipant`  
Remove a participant from all groups

`/checkadmin`  
Check if you are the admin
