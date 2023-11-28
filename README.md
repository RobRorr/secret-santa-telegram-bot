# secret-santa-telegram-bot
A simple Telegram bot that manages the Secret Santa for a single group. 

# Usage
Each participant must add themselves to the list using the private Telegram chat with the bot. 
It uses chat IDs and a json file to reconize and manage the participants.

# Configuration
Modify the config.ini file before starting.
```
JSON_FILE_PATH = your_json_file_path
TELEGRAM_TOKEN = your_telegram_token
ADMIN = your_chat_id
```
If you need to know how to start a bot, you can find the information at [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).

# Commands

###### All Users

`/start`  
Send a personal message

`/help`  
Describe usage

`/addme`  
Add user to secret santa list

`/removeme`  
Remove user from secret santa list

###### Admin
`/startsecretsanta`  
Send messagge to all participants with recipient's name and wishlist

`/removeall`  
Clear the secret santa list

`/removeparticipant`  
Remove a participant from the secret santa list
