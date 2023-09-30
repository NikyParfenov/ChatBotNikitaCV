import enum
from utils.db_engine import SessionMaker
from models.db_models import ChatMessages


class DBActions(str, enum.Enum):
    ADD_MESSAGE = 'add_message'
    GET_MESSAGES = 'get_message'
    GET_CHATS = 'get_chats'


def database_action(action: DBActions, **kwargs):

    session = SessionMaker()

    match action:
        case DBActions.ADD_MESSAGE:
            msg = ChatMessages()
            msg.chat_id = kwargs['chat_id']
            msg.message_id = kwargs['message_id']
            msg.role = kwargs['role']
            msg.content = kwargs['content']
            session.add(msg)
            sql_query = msg

        case DBActions.GET_MESSAGES:
            query = session.query(ChatMessages).filter(ChatMessages.chat_id == kwargs['chat_id'])
            sql_query = query.order_by(ChatMessages.created_at).all()

        case DBActions.GET_CHATS:
            sql_query = session.query(ChatMessages.chat_id).distinct().all()

        case _:
            raise Exception(f'Unknown DB action {action}')

    session.commit()
    session.close()

    return sql_query
