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

        except openai.error.Timeout as e:
            retry_time = e.retry_after if hasattr(e, 'retry_after') else 3
            logger.info(f"Timeout error occurred. Retrying in {retry_time} seconds...")
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
