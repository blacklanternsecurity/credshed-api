#!/usr/bin/env python3

# by TheTechromancer

import json
import logging
from . import util
from pathlib import Path
from hashlib import sha512

# set up logging
log = logging.getLogger('credshed.api.auth')


db_dir = Path(__file__).parent.resolve() / 'db'
db_dir.mkdir(exist_ok=True)
db_filename = db_dir / 'users.db'



def identity(payload):

    log.critical('identity()')

    user_id = payload['identity']
    return user_lookup_by_id(user_id)



def user_lookup(username, password):
    '''
    DB lookup goes here
    please don't hard-code credentials
    '''

    username = str(username)
    password = str(password)

    # if username and password are reasonable values
    if username.isalnum() and len(password) > 0:

        # and creds are valid
        password_hash = sha512(password.encode()).hexdigest()

        try:
            with open(db_filename, 'r') as db_file:
                db = json.load(db_file)
                if username in db:
                    if db[username] == password_hash:
                        return True

        except (EOFError, FileNotFoundError):
            log.error(f'Database not found at {db_filename}')


    return False



def create_default_user():

    log.warning(f'Creating new users database at {db_filename}')

    with open(db_filename, 'w') as db_file:

        db = dict()

        # admin / random 14-character password
        default_username = 'admin'
        default_password = util.random_password(14)

        db[default_username] = sha512(default_password.encode()).hexdigest()
        json.dump(db, db_file)

    return (default_username, default_password)