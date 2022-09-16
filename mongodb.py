import functools
from pymongo.errors import CollectionInvalid


def handle_errors():
    def wrap(func):
        @functools.wraps(func)
        def run_func(db, collection_name, *args):
            while True:
                try:
                    return func(db, collection_name, *args)
                except CollectionInvalid:
                    return f'collection {collection_name} is exist'
                except ConnectionError:
                    continue
                finally:
                    pass
        return run_func
    return wrap


@handle_errors()
def create_collection(db, collection_name):
    db.create_collection(collection_name)
    return f'collection {collection_name} was created'


@handle_errors()
def drop_collection(db, collection_name):
    db.drop_collection(collection_name)
    return f'collection {collection_name} was droped'


@handle_errors()
def write_elements(db, collection_name, elements):
    db[collection_name].insert_many(elements)
    return f'write {db[collection_name].count_documents({})} documents into {collection_name} collection'


@handle_errors()
def get_elements(db, collection_name, filters):
    elements = []
    for filter in filters:
        elements = [*elements, *[entry for entry in db[collection_name].find(filter)]]
    return elements
