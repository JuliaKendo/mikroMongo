import sys
import logging
import functools
from environs import Env
from bson.json_util import dumps, loads
from flask import Flask, render_template, request

import settings
from notify_rollbar import notify_rollbar
from exceptions import (
    SLUG_TO_EXCEPTIONS_TITLE as slugs_of_failure,
    get_slug_of_failure
)
from mongodb import (
    get_server_info,
    show_statistics,
    create_collection,
    drop_collection,
    write_elements,
    get_elements,
    update_elements,
    delete_elements
)

logger = logging.getLogger('mongodb_api')

env = Env()
env.read_env()

app = Flask(__name__)

commands = {
    'SHOW': show_statistics,
    'CREATE': create_collection,
    'DROP': drop_collection,
    'INSERT': write_elements,
    'FIND': get_elements,
    'UPDATE': update_elements,
    'DELETE': delete_elements
}


def handle_errors():
    def wrap(func):
        @functools.wraps(func)
        def run_func():
            try:
                return func()
            except Exception as exe:
                title_of_error = slugs_of_failure.get(
                    get_slug_of_failure(exe), ''
                )
                logger.exception(title_of_error)
                return title_of_error

        return run_func
    return wrap


@app.route('/')
def show_main_page():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
@notify_rollbar()
def get_db_info():
    return get_server_info(env.str('DB_CONNECTION_STRING'))


@app.route('/statistic', methods=['POST'])
@notify_rollbar()
@handle_errors()
def handle_statistic():
    request_params = request.json['params']
    action, *__ = request_params.split('&')
    collections_info = commands[action.strip().upper()](
        env.str('DB_CONNECTION_STRING'),
        env.str('DB_NAME'),
    )
    return collections_info


@app.route('/collection', methods=['POST'])
@notify_rollbar()
@handle_errors()
def handle_collection():
    request_params = request.json['params']
    collection_name, action, *__ = request_params.split('&')
    collection_info = commands[action.strip().upper()](
        env.str('DB_CONNECTION_STRING'),
        env.str('DB_NAME'),
        collection_name.strip()
    )
    return collection_info


@app.route('/entries', methods=['POST'])
@notify_rollbar()
@handle_errors()
def handle_entries():
    request_params = request.json['params']
    collection_name, action, *entries = request_params.split('&')
    command = action.strip().upper()
    params = [loads(entry) for entry in entries]
    if command == 'UPDATE':
        entries_info = commands[command](
            env.str('DB_CONNECTION_STRING'),
            env.str('DB_NAME'),
            collection_name.strip(),
            filter=params[0], elements=params[1:]
        )
    else:
        entries_info = commands[command](
            env.str('DB_CONNECTION_STRING'),
            env.str('DB_NAME'),
            collection_name.strip(),
            elements=params
        )
    return dumps(entries_info)


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
