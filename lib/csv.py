#!/usr/bin/env python3

# by TheTechromancer

import csv


class Line():

    def __init__(self):
        self._line = None

    def write(self, line):
        self._line = line

    def read(self):
        return self._line



def iter_csv(accounts):

    line = Line()
    writer = csv.writer(line)
    writer.writerow(['Email', 'Username', 'Password', 'Hash', 'Misc/Description', 'Sources'])
    yield line.read()
    for account in accounts:
        writer.writerow([
            getattr(account, 'email', ''),
            getattr(account, 'username', ''),
            getattr(account, 'password', ''),
            ', '.join(getattr(account, 'hashes', [])),
            getattr(account, 'misc', ''),
            getattr(account, 'sources', '')
        ])
        yield line.read()


def csv_response(data):
    
    response = Response(iter_csv(data), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    return response