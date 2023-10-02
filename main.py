import os
import openai
import asyncio
import requests
import urllib.request
from telebot.async_telebot import AsyncTeleBot
from datetime import datetime
from telebot import apihelper, util, types
from dotenv import load_dotenv
from loguru import logger
from utils.logs_customize import logs_customize
from db_scripts import DBActions, database_action
from models.openai_models import gpt_completion, whisper_transcribe
from models.db_models import MessageRoles


if __name__ == '__main__':

    logs_customize()
    dotenv_path = '.env'
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    os.makedirs("./tmp", exist_ok=True) 
    apihelper.SESSION_TIME_TO_LIVE = 60 * 5
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    telegram_token = os.environ.get('TELEBOT_TOKEN')
    bot = AsyncTeleBot(telegram_token)

    markup = types.ReplyKeyboardMarkup()
    education = types.KeyboardButton('Education')
    experience = types.KeyboardButton('Experience')
    stack = types.KeyboardButton('Stack')
    contacts = types.KeyboardButton('Contacts')
    resume = types.KeyboardButton('Short CV')
    markup.row(education, experience, stack)
    markup.row(contacts, resume)

    def extract_arg(arg):
        return arg.split()[1:]

    def assistant_content(path: str = 'Information.txt'):
        with open(path, 'r') as file:
            assisstant_information = file.read()
        assistant_description = [
            "1. You are assistant that conduct the dialog with users about Nikita Parfenov experience. ",
            "2. Try to answer with bullet/numeric points if possible.",
            "3. You should not answer on questions that doesn't concern Nikita Parfenov. ",
            "If the user asks about something that doesn't concern Nikita Parfenov ask the user to focus questions about Nikita. "
            "4. If you don't have the information about user prompt ask the user to clarify from Nikita Parfenov.",
            f"5. Today is {str(datetime.now().date())}."
        ]
        return '\n'.join(assistant_description) + '\n\n' + assisstant_information

    @logger.catch
    @bot.message_handler(commands=['start', 'help'])
    async def send_welcome(message):
        introduction = "Welcome to Resume AI Bot!\n\n" \
                       "I have the information about professional experience of Nikita Parfenov 👨‍💻\n" \
                       "You can ask questions about:\n" \
                       "- education\n" \
                       "- experience\n" \
                       "- programming stack\n" \
                       "- contacts\n" \
                       "- hobbies\n" \
                       "- area of interests\n" \
                       "... and other\n\n" \
                       "You can choose predefined questions by clicking a button below or ask your own question.\n" \
                       "You can ask your questions either by voice 🔊 or text 📝\n\n" \
                       "Chat maintains different languages 🇺🇸🇪🇸🇩🇪🇫🇷🇮🇹🇷🇺...\n\n" \
                       "Enjoy! :)"
        await bot.send_message(message.chat.id, introduction, reply_markup=markup)
        await bot.delete_message(message.chat.id, message.message_id)

    @logger.catch
    @bot.message_handler(commands=['get_chats'])
    async def get_chats(message):
        chats_from_db = [str(chat.chat_id) for chat in database_action(action=DBActions.GET_CHATS)]
        chats_string = '\n'.join(chats_from_db)
        await bot.send_message(message.chat.id, text=f'CHATS:\n{chats_string}')


    @logger.catch
    @bot.message_handler(commands=['get_chat_messages'])
    async def get_chat_messages(message):
        status = extract_arg(message.text)
        try:
            chat_id = int(status[0])
            messages_from_db = database_action(action=DBActions.GET_MESSAGES, chat_id=chat_id)
            msg_list = []
            for msg in messages_from_db:
                msg_list.append(str(msg.retrieve_msg()))
            response = '\n'.join(msg_list)
        except Exception:
            response = 'Empty'

        splitted_text = util.smart_split(response, 4000)
        for text in splitted_text:
            await bot.send_message(message.chat.id, text=f'MESSAGES:\n{text}')


    @logger.catch
    @bot.message_handler(commands=['help_dev'])
    async def helper(message):
        instructions = "Input can be a text, audio or voice (mp3, mp4, mpeg, mpga, m4a, wav, webm)\n\n" \
                       "Commands:\n" \
                       "/help_dev - show commands\n" \
                       "/get_chats - show chats\n" \
                       "/get_chat_messages X - show messages of X chat_id"
        await bot.reply_to(message, instructions)
        

    @logger.catch
    @bot.message_handler(content_types=['audio', 'voice'])
    async def transcribe_audio(message):
        match message.content_type:
            case 'audio':
                file_info = await bot.get_file(message.audio.file_id)
            case 'voice':
                file_info = await bot.get_file(message.voice.file_id)

        # Transcribe the message
        audio_url = 'https://api.telegram.org/file/bot{}/{}'.format(telegram_token, file_info.file_path)
        response = requests.get(audio_url)
        local_filename, _ = urllib.request.urlretrieve(audio_url, filename=f"./tmp/{response.url.split('/')[-1]}")
        transcription = whisper_transcribe(local_filename)
        os.remove(local_filename)

        # Run text processing
        message.text = transcription
        message.message_id = message.message_id
        await echo_all(message)


    @logger.catch
    @bot.message_handler(func=lambda msg: True)
    async def echo_all(message):
        db_data = {
            "chat_id": message.chat.id,
            "message_id": message.message_id,
            "role": MessageRoles.USER,
            "content": message.text,
        }
        database_action(action=DBActions.ADD_MESSAGE, **db_data)

        if message.text.startswith('/'):
            response = 'Unknown command'
            output_message = await bot.reply_to(message, response)
        else:
            await bot.send_chat_action(message.chat.id, 'typing')

            db_messages = database_action(action=DBActions.GET_MESSAGES, chat_id=message.chat.id)
            msg_list = []
            for msg in db_messages:
                msg_list.append(msg.to_openai())

            chat_context = [{"role": "system", "content": assistant_content()}, *msg_list[-3:]]
            response = gpt_completion(conversation=chat_context)
            output_message = await bot.send_message(message.chat.id, text=response)

        db_data = {
            "chat_id": message.chat.id,
            "message_id": output_message.message_id,
            "role": MessageRoles.ASSISTANT,
            "content": response,
        }
        database_action(action=DBActions.ADD_MESSAGE, **db_data)

    asyncio.run(bot.infinity_polling(timeout=10, long_polling_timeout=5))
