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
    user_caption = message.caption or ''

    encoded_image, amount_paid = asyncio.run(crop_killer(read_file_as_encode))

    if len(encoded_image):
        bot.delete_message(message.chat.id, message.message_id)  # delete the old recept

        get_user_order_history = get(message.from_user.id) or b':'
        [message_id, user_order] = get_user_order_history.decode().split(':')

        if user_caption:
            send_messages = user_caption + '|' + user_order + '|' + f'{str(amount_paid)}$' + ' ' + str(f'({username})')
        else:
            send_messages = user_order + '|' + f'{str(amount_paid)}$' + ' ' + str(f'({username})')

        # use try and except to avoid error if there is no message id
        try:
            reply_to_message_id = message_id
            bot.send_photo(message.chat.id, encoded_image, send_messages, reply_to_message_id=reply_to_message_id,disable_notification=True)

        except:
            bot.send_photo(message.chat.id, encoded_image, send_messages, disable_notification=True)


@bot.message_handler(content_types=['text'])
def listen_user_order(message):
    user_id = message.from_user.id
    text = str(message.text)

    patterns = [
        r'^(?:\d+\s*\+\s*rice)|(?:rice\s*\+\s*\d+)$',
        r'^rice$',
        r'^(?:[1-9]|1[0-5])$',
        r'\d+\s*\+\s*\d+',
        r'rice\s*x\s*[1-9]|1[0-5]',
        r'^rice\s*$',
    ]

    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            save(user_id, str(message.id) + ':' + text)
            break


if __name__ == "__main__":
    bot.infinity_polling()
