import logging
from .. import util
from . import json as json_reports
from . import html as html_reports
from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request

# set up logging
log = logging.getLogger('credshed.api.reporting')

api = Blueprint('reporting', __name__, template_folder='templates')


@api.route('/json/scraping/<int:days>', methods=['GET'])
@jwt_required
def scraping_report_json(days):

    return jsonify(json_reports.ScrapingReport(days=days))



@api.route('/html/scraping/<int:days>', methods=['GET'])
@jwt_required
def scraping_report_html(days):

    return html_reports.ScrapingReport(days=days).render()



@api.route('/email/scraping', methods=['POST'])
@jwt_required
def scraping_report_email():

    to = request.form.get('to')
    days = request.form.get('days', 7)
    if 'error' in params:
        return jsonify(params), 400

    email_report = html_reports.email.ScrapingReport(days=days)
    email_report.send(to=to)