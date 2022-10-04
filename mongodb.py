import pdb
import pprint
import functools
from contextlib import contextmanager, asynccontextmanager
from requests.exceptions import HTTPError
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid

import settings


def handle_errors():
    def wrap(func):
        @functools.wraps(func)
        def run_func(conn_str, db_name='', table_name='', **kwargs):
            while True:
                try:
                    return func(conn_str, db_name, table_name, kwargs)
                except CollectionInvalid:
                    return f'element {table_name} is exist'
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
def get_server_info(conn_str, *args, **kwargs):
    client = MongoClient(conn_str)
    return client.server_info()


@handle_errors()
def create_collection(conn_str, db_name, table_name, params):
    with open_db_connection(conn_str, db_name) as db:
        db.create_collection(table_name)
        return f'collection {table_name} was created'


@handle_errors()
def drop_collection(conn_str, db_name, table_name, params):
    with open_db_connection(conn_str, db_name) as db:
        db.drop_collection(table_name)
        return f'collection {table_name} was droped'


@handle_errors()
def show_statistics(conn_str, db_name, table_name, params):
    with open_db_connection(conn_str, db_name) as db:
        stat_info = []
        for table_name in db.list_collection_names():
            stat_info.append(f'table: {table_name}')
            stat_info.append(f' - {db[table_name].count_documents({})} items')
        return '\n'.join(stat_info)


@handle_errors()
def write_elements(conn_str, db_name, table_name, params):
    with open_db_connection(conn_str, db_name) as db:
        db[table_name].insert_many(params['elements'])
        return f'write {db[table_name].count_documents({})} items into {table_name}'


@handle_errors()
def get_elements(conn_str, db_name, table_name, params):
    elements = []
    with open_db_connection(conn_str, db_name) as db:
        for filter in params['elements']:
            elements = [*elements, *[entry for entry in db[table_name].find(filter)]]
    return elements


@handle_errors()
def update_elements(conn_str, db_name, table_name, params):
    modified_count = 0
    with open_db_connection(conn_str, db_name) as db:
        for element in params['elements']:
            update_result = db[table_name].update_many(params['filter'], element, upsert=True)
            modified_count += update_result.matched_count
        return f'update {modified_count} items into {table_name}'


@handle_errors()
def delete_elements(conn_str, db_name, table_name, params):
    deleted_count = 0
    with open_db_connection(conn_str, db_name) as db:
        for filter in params['elements']:
            delete_result = db[table_name].delete_many(filter)
            deleted_count += delete_result.deleted_count
        return f'delete {deleted_count} items from {table_name}'


# async tools:
def ahandle_errors():
    def wrap(func):
        @functools.wraps(func)
        async def run_func(conn_str, db_name='', table_name='', **kwargs):
            while True:
                try:
                    return await func(conn_str, db_name, table_name, kwargs)
                except CollectionInvalid:
                    return f'element {table_name} is exist'
                except (ConnectionError, HTTPError):
                    continue
        return run_func
    return wrap


@contextmanager
def aopen_db_connection(conn_str, db_name):
    if settings.database is None:
        client = AsyncIOMotorClient(conn_str)
        settings.database = client[db_name]
    yield settings.database


@ahandle_errors()
async def aget_server_info(conn_str, *args, **kwargs):
    client = AsyncIOMotorClient(conn_str)
    return await client.server_info()


@ahandle_errors()
async def acreate_collection(conn_str, db_name, table_name, params):
    with aopen_db_connection(conn_str, db_name) as db:
        await db.create_collection(table_name)
        return f'collection {table_name} was created'


@ahandle_errors()
async def adrop_collection(conn_str, db_name, table_name, params):
    with aopen_db_connection(conn_str, db_name) as db:
        await db.drop_collection(table_name)
        return f'collection {table_name} was droped'


@ahandle_errors()
async def ashow_statistics(conn_str, db_name, table_name, params):
    with aopen_db_connection(conn_str, db_name) as db:
        stat_info = []
        cursor = db.list_collection_names()
        for table_name in await cursor:
            count_documents = await db[table_name].count_documents({})
            stat_info.append(f'table: {table_name}')
            stat_info.append(f' - {count_documents} items')
        return '\n'.join(stat_info)


@ahandle_errors()
async def awrite_elements(conn_str, db_name, table_name, params):
    with aopen_db_connection(conn_str, db_name) as db:
        await db[table_name].insert_many(params['elements'])
        count_documents = await db[table_name].count_documents({})
        return f'write {count_documents} items into {table_name}'


@ahandle_errors()
async def aget_elements(conn_str, db_name, table_name, params):
    elements = []
    with aopen_db_connection(conn_str, db_name) as db:
        for filter in params['elements']:
            elements = [*elements, *[entry async for entry in db[table_name].find(filter)]]
    return elements


@ahandle_errors()
async def aupdate_elements(conn_str, db_name, table_name, params):
    modified_count = 0
    with aopen_db_connection(conn_str, db_name) as db:
        for element in params['elements']:
            update_result = await db[table_name].update_many(params['filter'], element, upsert=True)
            modified_count += update_result.matched_count
        return f'update {modified_count} items into {table_name}'


@ahandle_errors()
async def adelete_elements(conn_str, db_name, table_name, params):
    deleted_count = 0
    with aopen_db_connection(conn_str, db_name) as db:
        for filter in params['elements']:
            delete_result = await db[table_name].delete_many(filter)
            deleted_count += delete_result.deleted_count
        return f'delete {deleted_count} items from {table_name}'
