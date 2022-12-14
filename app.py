import sys
import logging
import functools
from environs import Env
from bson.json_util import dumps, loads
from quart import Quart, render_template, request

import settings
from notify_rollbar import anotify_rollbar
from exceptions import (
    SLUG_TO_EXCEPTIONS_TITLE as slugs_of_failure,
    get_slug_of_failure
)
from mongodb import (
    aget_server_info,
    ashow_statistics,
    acreate_collection,
    adrop_collection,
    awrite_elements,
    aget_elements,
    aupdate_elements,
    adelete_elements
)

logger = logging.getLogger('mongodb_api')
logging.basicConfig(
    filename='mikroMongo.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
)

env = Env()
env.read_env()

app = Quart(__name__)
settings.init()

commands = {
    'SHOW': ashow_statistics,
    'CREATE': acreate_collection,
    'DROP': adrop_collection,
    'INSERT': awrite_elements,
    'FIND': aget_elements,
    'UPDATE': aupdate_elements,
    'DELETE': adelete_elements
}


def handle_errors():
    def wrap(func):
        @functools.wraps(func)
        async def run_func():
            try:
                return await func()
            except Exception as exe:
                title_of_error = slugs_of_failure.get(
                    get_slug_of_failure(exe), ''
                )
                logger.exception(title_of_error)
                return title_of_error

        return run_func
    return wrap


@app.route('/')
async def show_main_page():
    return await render_template('index.html')


@app.route('/submit', methods=['POST'])
@anotify_rollbar()
async def get_db_info():
    return await aget_server_info(env.str('DB_CONNECTION_STRING'))


@app.route('/statistic', methods=['POST'])
@anotify_rollbar()
@handle_errors()
async def handle_statistic():
    request_params = await request.get_json()
    action, *__ = request_params['params'].split('&')
    collections_info = await commands[action.strip().upper()](
        env.str('DB_CONNECTION_STRING'),
        env.str('DB_NAME'),
    )
    return collections_info


@app.route('/collection', methods=['POST'])
@anotify_rollbar()
@handle_errors()
async def handle_collection():
    request_params = await request.get_json()
    collection_name, action, *__ = request_params['params'].split('&')
    collection_info = await commands[action.strip().upper()](
        env.str('DB_CONNECTION_STRING'),
        env.str('DB_NAME'),
        collection_name.strip()
    )
    return collection_info


@app.route('/entries', methods=['POST'])
@anotify_rollbar()
@handle_errors()
async def handle_entries():
    request_params = await request.get_json()
    collection_name, action, *entries = request_params['params'].split('&')
    command = action.strip().upper()
    params = [loads(entry) for entry in entries]
    if command == 'UPDATE':
        entries_info = await commands[command](
            env.str('DB_CONNECTION_STRING'),
            env.str('DB_NAME'),
            collection_name.strip(),
            filter=params[0], elements=params[1:]
        )
    else:
        entries_info = await commands[command](
            env.str('DB_CONNECTION_STRING'),
            env.str('DB_NAME'),
            collection_name.strip(),
            elements=params
        )
    return dumps(entries_info)


def main():

    logger.debug('Server start')
    try:
        app.run()
    except KeyboardInterrupt:
        sys.stderr.write('Server shut down')
    logger.debug('Server shut down')


if __name__ == '__main__':
    main()
