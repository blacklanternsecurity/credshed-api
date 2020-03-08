#!/usr/bin/env python3

# by TheTechromancer

import string
import random

def random_password(length=32):

    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def stringify_json(json):

    new_json = dict()
    for k,v in json.items():
        if not type(v) == dict:
            new_json[k] = str(v)
        else:
            new_json[k] = stringify_json(v)

    return new_json


def get_params(request, required=[], optional=[]):
    '''
    Attempts to retrieve JSON values from POST request
    If required params are missing, returns error message
    '''

    params = dict()

    try:
        for param in required:
            params[param] = request.json[param]
    except (TypeError, KeyError, AttributeError) as e:
        if type(e) == KeyError:
            msg = f'Missing parameter: {e}'
        else:
            msg = f'Error in request data: {e}'
        return {'error': msg}

    for param in optional:
        try:
            params[param] = reques.json[param]
        except (TypeError, KeyError, AttributeError):
            pass

    return params