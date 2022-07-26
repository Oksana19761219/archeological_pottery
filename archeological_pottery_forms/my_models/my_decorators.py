import time
import logging

logger = logging.getLogger(__name__)

def calculate_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.info(f'programa vykdyta {run_time} sek.')
    return wrapper