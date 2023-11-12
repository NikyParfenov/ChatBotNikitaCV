import os
import openai
import asyncio
import requests
import urllib.request
from telebot.async_telebot import AsyncTeleBot
from telebot import apihelper, util
from dotenv import load_dotenv
from loguru import logger
from utils.logs_customize import logs_customize
from db_scripts import DBActions, database_action
from models.openai_models import gpt_completion, whisper_transcribe
from models.db_models import MessageRoles
from vectorization import doc_vectorization
from context import assistant_content


# https://t.me/nikitatesetcasebot

if __name__ == '__main__':

    logs_customize()
    dotenv_path = '.env'
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    os.makedirs("./tmp", exist_ok=True) 
    apihelper.SESSION_TIME_TO_LIVE = 60 * 5
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    telegram_token = os.environ.get('TELEBOT_TOKEN')
    docsearch = doc_vectorization(token=openai.api_key)
    bot = AsyncTeleBot(telegram_token)

    def extract_arg(arg):
        return arg.split()[1:]

    @logger.catch
    @bot.message_handler(commands=['start', 'help'])
    async def send_welcome(message):
        introduction = "Добро пожаловать в Альфа-банк FAQ!\n\n" \
                       "Я могу помочь вам ответить на вопросы о кредитных и дебетовых картах, кредитах наличными или Алфа-Мобайл.\n" \
                       "Вы можете задавать вопросы как текстом, так и голосом."
        await bot.send_message(message.chat.id, introduction)
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

        # It's better to use Context window but for prototype let's put it in user msg
        docs = docsearch.similarity_search_with_score(message.text, k=5)
        docs_content = [f"[{i+1}] QUESTION: {doc[0].metadata['question']}; ANSWER: {doc[0].metadata['doc_content']}" for i, doc in enumerate(docs) if doc[1] < 0.47]
        user_content = message.text + '\n\nDOCUMENTS:\n' + '\n'.join(docs_content)

        db_data = {
            "chat_id": message.chat.id,
            "message_id": message.message_id,
            "role": MessageRoles.USER,
            "content": user_content,
        }
        database_action(action=DBActions.ADD_MESSAGE, **db_data)

        await bot.send_chat_action(message.chat.id, 'typing')
        db_messages = database_action(action=DBActions.GET_MESSAGES, chat_id=message.chat.id)
        msg_list = []
        for msg in db_messages:
            msg_list.append(msg.to_openai())

        # Load las user-assistant messages to take into account dependable questions.
        # 5 steps history sometimes can exceed 4k tokens limit, so, wrap it in exception
        try:
            chat_context = [{"role": "system", "content": assistant_content()}, *msg_list[-5:]]
            response = gpt_completion(conversation=chat_context)
        except openai.error.InvalidRequestError:
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

    async def run():
        await bot.polling(non_stop=True)

    asyncio.run(run())
