import functools
import time
import openai
from datetime import timedelta
from time import perf_counter
from loguru import logger


def wrap_exception(func):

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except openai.error.RateLimitError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 3
            logger.info(f"Rate limit exceeded. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return func(*args, **kwargs)

        except openai.error.APIError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 3
            logger.info(f"API error occurred. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return func(*args, **kwargs)

        except openai.error.ServiceUnavailableError as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 3
            logger.info(f"Server error occurred. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return func(*args, **kwargs)

        except OSError as e:
            retry_time = 5  # Adjust the retry time as needed
            logger.info(f"Connection error occurred: {e}. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return func(*args, **kwargs)

        except RuntimeError as e:
            retry_time = 5  # Adjust the retry time as needed
            logger.info(f"Service error occurred: {e}. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return func(*args, **kwargs)

    return wrapped


def dead_chat_wrapper(func):

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        # chat_id is only for logs
        chat_id = kwargs.get('chat_id') if kwargs.get('chat_id') else 'N/A'
        try:
            start = perf_counter()
            response = func(*args, **kwargs)
            end = perf_counter()
            logger.info(f'Chat_id: {chat_id}; Response time: {str(timedelta(seconds=end - start))}')
        except (TypeError, openai.error.RateLimitError, openai.error.APIError, openai.error.ServiceUnavailableError) as e:
            response = 'Sorry, something went wrong. Could you please repeat your query?'
            logger.warning(f'Chat_id: {chat_id}; Error: {e}; Chat response: {response}')
        except openai.error.InvalidRequestError as e:
            response = "Sorry, I still can't store a lot of information, could you make your question more compact?"
            logger.warning(f'Chat_id: {chat_id}; Error: {e}; Chat response: {response}')
        return response
    return wrapped
