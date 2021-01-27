import logging
from flask import render_template
from .. import json as json_reports

# set up logging
log = logging.getLogger('credshed.api.reporting.html')


class HTMLReport:

    # override in child class
    data_source = json_reports.JSONReport

    # override in child class
    template = 'report'

    def __init__(self, *args, **kwargs):

        self._json = self.data_source(*args, **kwargs)


    @property
    def json(self):
        '''
        Override in child class if additional data/processing is required
        '''

        return self._json


    def render(self):

        return render_template(f'html/{self.template}.html', **self.json)




class ScrapingReport(HTMLReport):

    data_source = json_reports.ScrapingReport
    template = 'scraping_report'

