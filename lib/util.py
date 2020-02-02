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
