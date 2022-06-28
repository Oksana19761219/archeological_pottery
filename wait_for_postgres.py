import os
import logging
from time import time, sleep
import psycopg2
from mysite.settings import PASSWORD


check_timeout = os.getenv('POSTGRES_CHECK_TIMEOUT', 30)
check_interval = os.getenv('POSTGRES_CHECK_INTERVAL', 1)


config = {
    'dbname': os.getenv('POSTGRES_DB', 'pottery_forms'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', PASSWORD),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.info(
    f"DB config {config['dbname']} {config['user']} {config['host']} ...")


start_time = time()


def pg_isready(host, user, password, dbname, port):
    while time() - start_time < check_timeout:
        try:
            conn = psycopg2.connect(**vars())
            logger.info('Postgres is ready')
            conn.close()
            return True
        except psycopg2.OperationalError:
            logger.info(
                f"Postgres isn't ready. Waiting for {check_interval} sec...")
            sleep(check_interval)

    logger.error(
        f'We could not connect to Postgres within {check_timeout} seconds.')
    return False

pg_isready(**config)