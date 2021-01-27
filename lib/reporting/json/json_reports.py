import logging
from ... import util
from pathlib import Path
from ...credshed import *
from datetime import datetime, timedelta
from flask_jwt_extended import get_jwt_identity


# set up logging
log = logging.getLogger('credshed.api.reporting.json')


class JSONReport(dict):
    '''
    Represents JSON-like report data
    '''
    
    def __init__(self, *args, **kwargs):

        self._credshed = CredShed()
        self.update(self._execute_query(*args, **kwargs))


    def _execute_query(self, *args, **kwargs):
        '''
        Times query and includes time elapsed in results
        '''

        start_time = datetime.now()

        report_data = self._query(*args, **kwargs)

        end_time = datetime.now()
        time_elapsed = (end_time - start_time)

        return {
            'report': report_data,
            'elapsed': f'{time_elapsed.total_seconds():.2f}',
        }


    def _query(self, *args, **kwargs):
        '''
        Return a dictionary containing report data
        Override in child class
        '''

        # do custom stuff
        return dict()


    @staticmethod
    def summarize_counts(l):
        '''
        Given an iterator of dictionaries in the format of:
            {key1: int1}, {key1: int2} ...
        Return a combined dictionary where int == the sum of other ints with the same str
            {key1: int1+int2, ...}
        '''
        summarized_counts = dict()
        for d in l:
            for k,c in d.items():
                try:
                    summarized_counts[k] += c
                except KeyError:
                    summarized_counts[k] = c
        return summarized_counts


    @staticmethod
    def top_results(d, limit=10, key=lambda x: x[-1], reverse=True):
        '''
        Given a dictionary, return the top "limit" results
        Sorting, by default, is performed by value in descending order
        '''

        l = list(d.items())
        l.sort(key=key, reverse=reverse)
        return dict(l[:limit])



class SourceReport(JSONReport):

    def _query(self, source_id):

        source = self._credshed.db.sources.find_one({
            'source_id': source_id
        })

        if config['FILESTORE']['store_dir'] and source['name']:
            source['name'] = str(Path(source['name']).relative_to(config['FILESTORE']['store_dir']))

        return source



class SourcesReport(JSONReport):

    def __init__(self, *args, **kwargs):

        self.days = kwargs['days']
        super().__init__(*args, **kwargs)


    def _query(self, regex, days=None):
        '''
        days = how many days to go back
        return all sources if None
        '''

        query = {
            'name': {
                '$regex': regex
            }
        }

        if days is not None:
            first_day = datetime.now() - timedelta(days=days)
            query['modified_date'] = {
                '$gt': first_day,
            }

        log.debug(f'Generating Sources Report for {get_jwt_identity()}')
        log.debug(f'Raw query: "{query}"')

        return list(self._credshed.db.sources.find(query))


class SearchStatsReport(JSONReport):

    def _query(self, query, limit=100):

        sources = self._credshed.query_stats(query, limit=limit)
        resolved_sources = dict()
        for source_id, count in sources:
            try:
                source_name = str(self._credshed.get_source(source_id))
            except errors.CredShedError as e:
                log.error(f'Failed to create source: {e}')
                continue
            resolved_sources[source_name] = count

        return dict(resolved_sources)



class ScrapingReport(SourcesReport):

    def _query(self, days=7, limit=10):

        regex = r'.*\d{4}-\d{2}-\d{2}_pastebin_[a-zA-Z0-9_]*\.txt'

        recent_leaks = super()._query(regex, days=days)
        recent_leaks.sort(key=lambda x: x['unique_accounts'], reverse=True)

        top_domains = [d['top_domains'] for d in recent_leaks]
        top_words = [d['top_words'] for d in recent_leaks]

        return {
            'largest_leaks': recent_leaks[:limit],
            'total_accounts': sum([l['total_accounts'] for l in recent_leaks]),
            'total_unique_accounts': sum([l['unique_accounts'] for l in recent_leaks]),
            'top_domains': self.top_results(self.summarize_counts(top_domains)),
            'top_words': self.top_results(self.summarize_counts(top_words))
        }