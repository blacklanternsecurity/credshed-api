#!/usr/bin/env python3

# by TheTechromancer

from . import util
from pathlib import Path



def get_secret_key():

    db_folder = Path(__file__).parent.resolve() / 'db'
    db_folder.mkdir(exist_ok=True)

    try:
        with open(str(db_folder / 'flask_secret.key'), 'rb') as f:
            secret_key = f.read()
            if len(secret_key) != 32:
                raise EOFError

    except (FileNotFoundError, EOFError):
        with open(str(db_folder / 'flask_secret.key'), 'wb') as f:
            # random 32-character secret
            secret_key = util.random_password(32).encode()
            f.write(secret_key)

    return secret_key