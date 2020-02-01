#!/usr/bin/env python3

# by TheTechromancer

import logging
from flask import escape
from datetime import datetime
from .credshed import CredShed, validation, errors


# set up logging
log = logging.getLogger('credshed.api.search')


cred_shed = CredShed()


def credshed_search(query, limit=0):
    '''
    returns (search_report, results)
    '''

    accounts = []

    num_accounts_in_db = cred_shed.db.account_count()

    query_type = validation.validate_query_type(query)

    num_results = 0
    start_time = datetime.now()

    for account in cred_shed.search(query, query_type=query_type, limit=limit):
        accounts.append({k: escape(v) for k,v in account.json.items()})

    end_time = datetime.now()
    time_elapsed = (end_time - start_time)

    json_response = {
        'stats': {
            'limit': f'{limit:,}',
            'query': escape(query),
            'query_type': query_type,
            'count': f'{len(accounts):,}',
            'searched': f'{num_accounts_in_db:,}',
            'elapsed': f'{time_elapsed.total_seconds():.2f}',
        },
        'accounts': accounts
    }

    return json_response


def credshed_search_stats(query, limit=10):
    '''
    returns (search_report, results)
    '''

    start_time = datetime.now()

    sources = cred_shed.query_stats(query, limit=limit)
    resolved_sources = dict()
    for source_id, count in sources:
        try:
            source_name = str(cred_shed.get_source(source_id))
        except errors.CredShedError as e:
            log.error(f'Failed to create source: {e}')
            continue
        resolved_sources[source_name] = count

    end_time = datetime.now()
    time_elapsed = (end_time - start_time)

    json_response = {
        'sources': dict(resolved_sources),
        'elapsed': f'{time_elapsed.total_seconds():.2f}',
    }

    return json_response


def credshed_get_source(source_id):

    return {k: str(v) for k,v in cred_shed.get_source(source_id).to_doc().items()}