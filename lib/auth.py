#!/usr/bin/env python3

# by TheTechromancer

import json
import logging
from . import util
from pathlib import Path
from .config import config
from hashlib import sha512

from ldap3 import Server, Connection, SAFE_SYNC
from ldap3.core.exceptions import LDAPException


# set up logging
log = logging.getLogger('credshed.api.auth')


db_dir = Path(__file__).parent.resolve() / 'db'
db_dir.mkdir(exist_ok=True)
db_filename = db_dir / 'users.db'


def ldap_user_lookup(username, password):

    if config['ldap']['server']:
        log.debug(f'Attempting to authenticate LDAP user {username}')

        ldap_username = f'{username}@' + config['ldap']['domain']

        try:
            server = Server(
                config['ldap']['server'],
                port=config['ldap']['port'],
                use_ssl=config['ldap']['tls']
            )
            conn = Connection(
                server,
                ldap_username,
                password,
                client_strategy=SAFE_SYNC,
                auto_bind=True
            )
            #status, result, response, _ = conn.search(
            #    config['ldap']['base'],
            #    f'(&(objectclass=user)(samAccountName={username}))'
            #)
            #dn = result[0]['dn']
            #log.debug(f'Successful LDAP login from {dn}')
            return True
        except (LDAPException, KeyError, IndexError) as e:
            log.error(e.args)

    return False


def local_user_lookup(username, password):

    username = str(username)
    password = str(password)

    # if username and password are reasonable values
    if username.isalnum() and len(password) > 0:

        # and creds are valid
        password_hash = sha512(password.encode()).hexdigest()

        db = load_user_db()
        if username in db:
            if db[username] == password_hash:
                return True

    return False


def load_user_db():

    db = {}
    try:
        with open(db_filename, 'r') as db_file:
            db = json.load(db_file)

    except (EOFError, FileNotFoundError):
        log.error(f'Database not found at {db_filename}')
        create_default_user()
        return load_user_db()

    return db



def user_lookup(username, password):

    return local_user_lookup(username, password) or ldap_user_lookup(username, password)




def create_default_user():

    log.warning(f'Resetting admin password')

    with open(db_filename, 'w') as db_file:

        db = load_user_db()
        if not db:
            log.warning(f'Creating new users database at {db_filename}')

        # admin / random 14-character password
        default_username = 'admin'
        default_password = util.random_password(14)

        db[default_username] = sha512(default_password.encode()).hexdigest()
        json.dump(db, db_file)

    return (default_username, default_password)