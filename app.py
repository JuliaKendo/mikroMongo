import logging
import sys
from environs import Env
from contextlib import suppress
from pymongo import MongoClient
from bson.json_util import dumps, loads
from flask import Flask, render_template, request

from mongodb import (
    create_collection,
    drop_collection,
    write_elements,
    get_elements
)

logger = logging.getLogger('mongodb_api')

env = Env()
env.read_env()

app = Flask(__name__)

client = MongoClient(
    env.str('DB_CONNECTION_STRING')
)
db = client[env.str('DB_NAME')]


@app.route('/')
def show_main_page():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def get_db_info():
    return client.server_info()


@app.route('/collection', methods=['POST'])
def handle_collection():
    with suppress(ValueError, TypeError, NameError):
        actions = {'CREATE': create_collection, 'DROP': drop_collection}
        params = request.json['params']
        collection_name, action, *__ = params.split('&')
        collection_info = actions[action.strip().upper()](db, collection_name.strip())
        return collection_info
    logger.exception('Unsupported query params')
    return 'Check query params'


@app.route('/entries', methods=['POST'])
def handle_entries():
    with suppress(ValueError, TypeError, NameError):
        actions = {'INSERT': write_elements, 'FIND': get_elements}
        params = request.json['params']
        collection_name, action, *entries = params.split('&')
        entries_info = actions[action.strip().upper()](
            db, collection_name.strip(), [loads(entry) for entry in entries]
        )
        return dumps(entries_info)
    logger.exception('Unsupported query params')
    return 'Check query params'


def main():
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
