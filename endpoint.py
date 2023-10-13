import os
import uvicorn
import openai
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from models.db_models import MessageRoles
from db_scripts import DBActions, database_action
from fastapi.responses import JSONResponse, HTMLResponse
from models.openai_models import gpt_completion
from context import assistant_content


class Data(BaseModel):
    content: str


app = FastAPI()

dotenv_path = '.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

openai.api_key = os.environ.get('OPENAI_API_KEY')


@app.post('/api/upload-text/')
def service_endpoint(data: Data):
    db_data = {
        "chat_id": 0,
        "message_id": 0,
        "role": MessageRoles.USER,
        "content": data.content,
    }
    database_action(action=DBActions.ADD_MESSAGE, **db_data)

    db_messages = database_action(action=DBActions.GET_MESSAGES, chat_id=message.chat.id)
    msg_list = []
    for msg in db_messages:
        msg_list.append(msg.to_openai())

    chat_context = [{"role": "system", "content": assistant_content()}, *msg_list[-3:]]
    response = gpt_completion(conversation=chat_context)

    db_data = {
        "chat_id": 0,
        "message_id": 0,
        "role": MessageRoles.ASSISTANT,
        "content": response,
    }
    database_action(action=DBActions.ADD_MESSAGE, **db_data)
    return JSONResponse(content={'response': response})


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
