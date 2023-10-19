import redis
import os

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_AUTH_PASS = os.environ.get('REDIS_AUTH_PASS')

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username="default", password=REDIS_AUTH_PASS)


def save(key, new_message):
    expiration_time = 14400  # 3hour

    check_data = r.get(key)
    if check_data:
        [_, old_order_message] = check_data.decode().split(':')
        r.set(key, str(new_message) + '|' + str(old_order_message))
    else:
        r.set(key, new_message, ex=expiration_time)
        return 'DONE'


def get(key):
    return r.get(key)
