from json.decoder import JSONDecodeError
from pymongo.errors import CollectionInvalid

SLUG_TO_EXCEPTIONS_TITLE = {
    'unsupported_query_error': 'unsupported params, check query params',
    'unsupported_command_error': 'unsupported command for the api query',
    'collection_invalid': 'element is not exist',
    'json_decode_error': 'can not decode json'
}


def get_slug_of_failure(exe):

    if isinstance(exe, CollectionInvalid):
        return 'collection_invalid'
    elif isinstance(exe, JSONDecodeError):
        return 'json_decode_error'
    elif isinstance(exe, KeyError):
        return 'unsupported_command_error'
    elif isinstance(exe, (ValueError, TypeError, NameError)):
        return 'unsupported_query_error'

    if hasattr(exe, 'slug'):
        return exe.slug

    return 'unknown_error'
