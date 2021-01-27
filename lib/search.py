#!/usr/bin/env python3

# by TheTechromancer

import logging
from . import util
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
    num_sources_in_db = cred_shed.db.source_count()

    query_type = validation.validate_query_type(query)

    num_results = 0
    start_time = datetime.now()

    for account in cred_shed.search(query, query_type=query_type, limit=limit):

        num_results += len(getattr(account, 'sources', []))

        account_dict = account.json
        hashes = account_dict.pop('h', [])
        source_ids = account_dict.pop('s', [])

        # sanitize the rest        
        #account_dict = {k: escape(v) for k,v in account_dict.items()}

        # sanitize hashes
        #account_dict['h'] = [escape(h) for h in hashes]
        account_dict['h'] = list(hashes)

        # sanitize source IDs
        account_dict['s'] = []
        for source_id in source_ids:
            try:
                account_dict['s'].append(int(source_id))
            except ValueError:
                continue
        
        accounts.append(account_dict)

    end_time = datetime.now()
    time_elapsed = (end_time - start_time)

    json_response = {
        'stats': {
            'limit': limit,
            'query': escape(query),
            'query_type': query_type,
            'unique_count': len(accounts),
            'total_count': num_results,
            'accounts_searched': num_accounts_in_db,
            'sources_searched': num_sources_in_db,
            'elapsed': f'{time_elapsed.total_seconds():.2f}',
        },
        'accounts': accounts
    }

    return json_response