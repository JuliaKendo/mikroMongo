import logging
import sys
from environs import Env
from contextlib import suppress
from bson.json_util import dumps, loads
from flask import Flask, render_template, request

import settings
from notify_rollbar import notify_rollbar
from mongodb import (
    get_server_info,
    create_collection,
    drop_collection,
    write_elements,
    get_elements
)

logger = logging.getLogger('mongodb_api')

env = Env()
env.read_env()

app = Flask(__name__)


@app.route('/')
def show_main_page():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
@notify_rollbar()
def get_db_info():
    return get_server_info(env.str('DB_CONNECTION_STRING'))


@app.route('/collection', methods=['POST'])
@notify_rollbar()
def handle_collection():
    with suppress(ValueError, TypeError, NameError):
        actions = {'CREATE': create_collection, 'DROP': drop_collection}
        params = request.json['params']
        collection_name, action, *__ = params.split('&')
        collection_info = actions[action.strip().upper()](
            env.str('DB_CONNECTION_STRING'),
            env.str('DB_NAME'),
            collection_name.strip()
        )
        return collection_info
    logger.exception('Unsupported query params')
    return 'Check query params'


@app.route('/entries', methods=['POST'])
@notify_rollbar()
def handle_entries():
    with suppress(ValueError, TypeError, NameError):
        actions = {'INSERT': write_elements, 'FIND': get_elements}
        params = request.json['params']
        collection_name, action, *entries = params.split('&')
        entries_info = actions[action.strip().upper()](
            env.str('DB_CONNECTION_STRING'),
            env.str('DB_NAME'),
            collection_name.strip(),
            [loads(entry) for entry in entries]
        )
        return dumps(entries_info)
    logger.exception('Unsupported query params')
    return 'Check query params'


def main():
    settings.init()
    logging.basicConfig(
        filename='mikroMongo.log',
        filemode='w',
        level=logging.DEBUG,
        format='%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
    )

    logger.debug('Server start')
    try:
        app.run()
    except KeyboardInterrupt:
        sys.stderr.write('Server shut down')
    logger.debug('Server shut down')


if __name__ == '__main__':
    main()
