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


env = Env()
env.read_env()

app = Flask(__name__)

client = MongoClient('0.0.0.0:27017')
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
    return 'Check query params'


if __name__ == '__main__':
    app.run()
