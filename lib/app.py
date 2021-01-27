#!/usr/bin/env python3

# by TheTechromancer


# misc
import string
import logging
from datetime import datetime
from urllib.parse import unquote_plus

# credshed
from . import auth
from .csv import *
from .search import *
from . import credshed
from . import security
from . import reporting

# flask
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
from flask import Flask, request, jsonify, escape, Response, stream_with_context, render_template
from flask_cors import CORS



# create the application object
api = Flask('credshed-api')

# handle CORS
CORS(api, supports_credentials=True)

# register reporting routes
api.register_blueprint(reporting.routes.api, url_prefix='/reports')

# secret key
api.secret_key = security.get_secret_key()
# set the secret key to sign the JWTs with
api.config['JWT_SECRET_KEY'] = api.secret_key

api.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
api.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
api.config['JWT_COOKIE_CSRF_PROTECT'] = False
# expires after 1 month
api.config['JWT_ACCESS_TOKEN_EXPIRES'] = 2592000

jwt = JWTManager(api)



# set up logging
log = logging.getLogger('credshed.api')



@api.route('/search', methods=['POST'])
@jwt_required
def search():
    '''
    given "query" parameter, returns accounts
    '''

    limit = 1000

    try:
        query = request.json.get('query', '').strip()
        log.info(f'Search query "{query}" by {get_jwt_identity()} from {request.remote_addr}')
        response = jsonify(credshed_search(query, limit=limit))
        return response

    except credshed.errors.CredShedError as e:
        log.error(f'Error executing search: {e}')
        response = jsonify({'error': str(e)})
        response.status_code = 400
        return response



@api.route('/search_stats/<query>', methods=['GET'])
@jwt_required
def search_stats(query):
    '''
    given "query" parameter, returns accounts
    '''

    try:
        query = query.strip()
        limit = min(1000, int(request.form.get('limit', 100)))
        log.info(f'Search stats query "{query}" by {get_jwt_identity()} from {request.remote_addr}')
        response = jsonify(reporting.json.SearchStatsReport(query, limit=limit))
        return response

    except (ValueError, credshed.errors.CredShedError) as e:
        log.error(f'Error executing search: {e}')
        response = jsonify({'error': str(e)})
        response.status_code = 400
        return response



@api.route('/source/<int:source_id>', methods=['GET'])
@jwt_required
def get_source(source_id):
    '''
    given "query" parameter, returns accounts
    '''

    try:
        log.info(f'Source query "{source_id}" by {get_jwt_identity()} from {request.remote_addr}')
        response = jsonify(reporting.json.SourceReport(source_id))
        return response

    except credshed.errors.CredShedError as e:
        log.error(f'Could not retrieve source "{source_id}": {e}')
        response = jsonify({'error': str(e)})
        response.status_code = 400
        return response



@api.route('/count', methods=['POST'])
@jwt_required
def count():
    '''
    given "query" parameter, returns count
    '''

    try:

        c = credshed.CredShed()
        query = request.form.get('query', '').strip()
        log.info(f'Count query for "{query}" by {get_jwt_identity()} from {request.remote_addr}')
        count = c.count(query)
        return jsonify({'count': count})

    except credshed.errors.CredShedError as e:
        log.error(f'Error executing search: {e}')
        response = jsonify({'search_report': f'Error executing search: {e}', 'error': True})
        response.status_code = 400
        return response



@api.route('/export_csv/<query>', methods=['GET'])
@jwt_required
def export_csv(query):
    '''
    given "query" parameter, returns CSV file containing accounts
    '''

    try:
        query = unquote_plus(query).strip()

        log.info(f'CSV download request for "{query}" by {get_jwt_identity()} from {request.remote_addr}')

        c = credshed.CredShed()
        accounts = c.search(query)

        query_str = ''.join([i for i in query if i.lower() in string.ascii_lowercase])
        filename = 'credshed_{}_{date:%Y%m%d-%H%M%S}.csv'.format( query_str, date=datetime.now() )

        return Response(stream_with_context(iter_csv(accounts)), content_type='text/csv', \
            headers={'Content-Disposition': f'attachment; filename={filename}'})

    except credshed.errors.CredShedError as e:
        log.error(str(e))



@api.route('/auth', methods=['POST'])
def _auth():

    username = request.json.get('username', 'UNKNOWN')
    password = request.json.get('password', 'UNSPECIFIED')

    bad_chars = ['(', ')', '&', '|', '<', '>']
    for c in bad_chars:
        username = username.replace(c, '')

    if auth.user_lookup(username, password) == True:
        
        access_token = create_access_token(identity=username)

        resp = jsonify({'login': True, 'access_token': access_token})

        # Set the JWT cookie in the response
        #set_access_cookies(resp, access_token)
        with api.app_context():
            #access_token = create_access_token(identity=username, expires_delta=False)
            resp.set_cookie('access_token_cookie', access_token)
        log.warning(f'Login attempt by {username} from {request.remote_addr} SUCCESSFUL')
        return resp, 200

    log.critical(f'Login attempt by {username} from {request.remote_addr} FAILED')
    return jsonify({'login': False}), 401



def create_api_token(username):

    with api.app_context():
        username = ''.join([c for c in username if c.lower() in string.ascii_lowercase])
        access_token = create_access_token(identity=username, expires_delta=False)
        return username, access_token