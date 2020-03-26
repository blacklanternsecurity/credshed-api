#!/usr/bin/env python3

# by TheTechromancer

import logging
import argparse
from lib import app
from lib import auth
from sys import stderr
from lib.credshed import logger


log = logging.getLogger('credshed.api')


if __name__ == '__main__':

    default_host = '127.0.0.1'
    default_port = 5007

    parser = argparse.ArgumentParser(description="REST API for CredShed")
    parser.add_argument('-ip', '--ip',      default=default_host,           help=f'IP address on which to listen (default: {default_host})')
    parser.add_argument('-p', '--port',     default=default_port, type=int, help=f'port on which to listen (default: {default_port})')
    parser.add_argument('-c', '--create-default-user', action='store_true', help='clear database and create default user (WARNING: OVERWRITES DB)')
    parser.add_argument('-j', '--create-jwt',                               help='create JWT token (for API) using given username')
    parser.add_argument('-d', '--debug',    action='store_true',            help='enable debugging')
 
    try:

        options = parser.parse_args()

        if options.debug:
            logging.getLogger('credshed').setLevel(logging.DEBUG)
            app.api.debug = True
        else:
            logging.getLogger('credshed').setLevel(logging.INFO)

        logger.listener.start()

        if options.create_default_user:
            default_username, default_password = auth.create_default_user()
            stderr.write('[+] Created default user:\n')
            stderr.write(f'      - Username: {default_username}\n')
            stderr.write(f'      - Password: {default_password}\n')

        elif options.create_jwt:
            username, api_token = app.create_api_token(options.create_jwt)
            stderr.write(f'[+] Created token for "{username}":\n')
            stderr.write(f'      - {api_token}\n')

        else:
            # start the server with the 'run()' method
            log.info(f'Credshed API running on http://{options.ip}:{options.port}')
            app.api.run(host=options.ip, port=options.port, debug=options.debug)

    except (argparse.ArgumentError, AssertionError) as e:
        log.critical(e)
        exit(2)

    except KeyboardInterrupt:
        log.error('Interrupted')
        exit(1)

    finally:
        try:
            logger.listener.stop()
        except:
            pass