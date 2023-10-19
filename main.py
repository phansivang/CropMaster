import telebot
from crop_killer import crop_killer
import os
import re
import asyncio
from cache import save, get

bot = telebot.TeleBot(os.environ.get('TELEGRAM_TOKEN'))


@bot.message_handler(content_types=['photo'])
def main(message):
    get_file_path = bot.get_file(message.photo[-1].file_id).file_path  # get file path from telegram bot

    read_file_as_encode = bot.download_file(get_file_path)  # encode file by using file path above

    username = f'{message.from_user.first_name} {message.from_user.last_name or ""}'
    # user_message_mention = (message.reply_to_message.text or '') if message.reply_to_message else ''

    encoded_image, amount_paid = asyncio.run(crop_killer(read_file_as_encode))

    if len(encoded_image):
        bot.delete_message(message.chat.id, message.message_id)  # delete the old recept

        get_user_order_history = get(message.from_user.id) or b':'
        [message_id, user_order] = get_user_order_history.decode().split(':')

        send_messages = user_order + '|' + f'{str(amount_paid)} USD' + ' ' + str(f'({username})')

        # use try and except to avoid error if there is no message id
        try:
            reply_to_message_id = message_id
            bot.send_photo(message.chat.id, encoded_image, send_messages, reply_to_message_id=reply_to_message_id, disable_notification=True)

        except:
            bot.send_photo(message.chat.id, encoded_image, send_messages, disable_notification=True)


@bot.message_handler(content_types=['text'])
def listen_user_order(message):
    user_id = message.from_user.id
    text = str(message.text)

    pattern_format = r'^(?:\d+\s*\+\s*rice)|(?:rice\s*\+\s*\d+)$'
    pattern_rice = r'^rice$'
    pattern_number = r'^(?:[1-9]|1[0-5])$'
    pattern_rice_and_number = r'\d+\s*\+\s*\d+'

    match_rice_and_number = re.match(pattern_rice_and_number, text)
    match_format = re.match(pattern_format, text)
    match_rice = re.match(pattern_rice, text)
    match_number = re.match(pattern_number, text)

    if match_format or match_rice or match_number or match_rice_and_number:
        save(user_id, str(message.id) + ':' + text)


if __name__ == "__main__":
    bot.infinity_polling()
