import telebot
from crop_killer import crop_killer
import os
import asyncio

bot = telebot.TeleBot(os.environ.get('TELEGRAM_TOKEN'))


@bot.message_handler(content_types=['photo'])
def main(message):
    get_file_path = bot.get_file(message.photo[-1].file_id).file_path  # get file path from telegram bot

    read_file_as_encode = bot.download_file(get_file_path)  # encode file by using file path above

    username = f'{message.from_user.first_name} {message.from_user.last_name or ""}'
    user_message_mention = (message.reply_to_message.text or '') if message.reply_to_message else ''

    encoded_image, amount_paid = asyncio.run(crop_killer(read_file_as_encode))

    if len(encoded_image):
        bot.delete_message(message.chat.id, message.message_id)  # delete the old recept

        send_messages = str(message.caption or user_message_mention) + '|' + f'{str(amount_paid)} USD' + ' ' + str(
            f'({username})')

        # use try and except to avoid error if reply_to_message key doesn't exist in message object
        try:
            reply_to = message.reply_to_message.message_id

            bot.send_photo(message.chat.id, encoded_image, send_messages, reply_to_message_id=reply_to, disable_notification=True)

        except:
            bot.send_photo(message.chat.id, encoded_image, send_messages, disable_notification=True)


if __name__ == "__main__":
    bot.infinity_polling()
