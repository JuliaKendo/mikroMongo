import functools
from contextlib import contextmanager
from requests.exceptions import HTTPError
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

import settings


def handle_errors():
    def wrap(func):
        @functools.wraps(func)
        def run_func(conn_str, db_name='', table_name='', *args):
            while True:
                try:
                    return func(conn_str, db_name, table_name, *args)
                except CollectionInvalid:
                    return f'collection {table_name} is exist'
                except (ConnectionError, HTTPError):
                    continue
        return run_func
    return wrap


@contextmanager
def open_db_connection(conn_str, db_name):
    if settings.database is None:
        client = MongoClient(conn_str)
        settings.database = client[db_name]
    yield settings.database


@handle_errors()
def get_server_info(conn_str, *args):
    client = MongoClient(conn_str)
    return client.server_info()


@handle_errors()
def create_collection(conn_str, db_name, table_name):
    with open_db_connection(conn_str, db_name) as db:
        db.create_collection(table_name)
        return f'collection {table_name} was created'


@handle_errors()
def drop_collection(conn_str, db_name, table_name):
    with open_db_connection(conn_str, db_name) as db:
        db.drop_collection(table_name)
        return f'collection {table_name} was droped'


@handle_errors()
def write_elements(conn_str, db_name, table_name, elements):
    with open_db_connection(conn_str, db_name) as db:
        db[table_name].insert_many(elements)
        return f'write {db[table_name].count_documents({})} documents into {table_name} collection'


@handle_errors()
def get_elements(conn_str, db_name, table_name, filters):
    elements = []
    with open_db_connection(conn_str, db_name) as db:
        for filter in filters:
            elements = [*elements, *[entry for entry in db[table_name].find(filter)]]
    return elements
