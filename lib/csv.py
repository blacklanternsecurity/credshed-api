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
    writer.writerow(['Email', 'Username', 'Password', 'Misc/Description'])
    yield line.read()
    for account in accounts:
        writer.writerow([f.decode() for f in [
            account.email,
            account.username,
            account.password,
            account.misc
        ]])
        yield line.read()


def csv_response(data):
    
    response = Response(iter_csv(data), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    return response