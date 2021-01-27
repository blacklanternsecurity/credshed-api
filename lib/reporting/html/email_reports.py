# email imports
import smtplib
from email.utils import make_msgid
from email.message import EmailMessage

# credshed
from .. import charts
from . import html_reports
from ...credshed import config
from .. import json as json_reports

# other
import logging
from datetime import datetime
from flask import render_template, Markup


# set up logging
log = logging.getLogger('credshed.api.reporting.email')


class EmailReport(html_reports.HTMLReport):

    # override these in child class
    subject = 'Email Report'
    template = 'email_report'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.images = {
            # image_name: img_tag,
            # ...
        }

        self.attachments = {
            # file_name: (file_bytes, maintype, subtype),
            # ...
        }
    

    @property
    def json(self):
        '''
        Data passed into self.template
        Override in child class
        '''
        json = super().json
        json.update({
            'images': Markup(self.images),
        })
        return json


    def attach_png(self, name, png_bytes):
        '''
        Attach a PNG file to the email
        '''

        # now create a Content-ID for the image
        # it looks like <long.random.number@xyz.com>
        # to use it as the img src, we don't need `<` or `>`
        # so we use [1:-1] to strip them off
        img_cid = make_msgid(domain='credshed.com')
        img_tag = f'<img src="cid:{img_cid[1:-1]}">'

        self.images[name] = img_tag
        self.attachments[name] = (png_bytes, 'image', 'png')



    def render(self):

        return render_template(f'email/{self.template}.html', **self.json)



    def send(self, to):
        '''
        Email the HTML report
        "to" can be either an email address or an array of them
        '''

        # either string or array is fine
        if type(to) == str:
            to = [to]

        # create the message
        self.msg = EmailMessage()

        # set the server settings
        try:
            self.msg['From'] = config['EMAIL ALERTS']['from']
            self.mail_server = config['EMAIL ALERTS']['mail_server']
            self.mail_port = config['EMAIL ALERTS']['mail_port']
            self.auth_user = config['EMAIL ALERTS']['auth_user']
            self.auth_pass = config['EMAIL ALERTS']['auth_pass']
        except KeyError as e:
            raise CredShedEmailError(f'Error parsing credshed.config: {e}')

        # set the plaintext body
        # TODO: make pretty
        self.msg.set_content(str(self.json))

        # set the HTML body
        message_body = self.render()
        msg.add_alternative(message_body, subtype='html')

        # attach files to message
        for name, (_bytes, maintype, subtype) in self.attachments.items():
            # now open the image and attach it to the email
            self.msg.get_payload()[1].add_related(_bytes, maintype=maintype, subtype=subtype, cid=file_cid)

        # the message is ready now

        # Send the message via our own SMTP server.
        # generic email headers
        self.msg['Subject'] = self.subject

        try:
            log.info('Connecting to email server')
            s = smtplib.SMTP(mail_server, mail_port)
            s.ehlo()
            s.starttls()
            s.login(self.auth_user, self.auth_pass)
            for email_address in to:
                log.info(f'Sending email to {email_address}')
                self.msg['To'] = f'<{email_address}>'
            s.send_message(self.msg)
            s.quit()
            log.info('Finished sending email')
        except smtplib.SMTPException as e:
            log.critical(f'Error sending email: {e}')



class ScrapingReport(EmailReport):

    data_source = json_reports.ScrapingReport
    template = 'scraping_report'

    def __init__(self, *args, **kwargs):

        self.days = kwargs['days']

        super().__init__(*args, **kwargs)

        # pie_data = list(self.json['report']['top_domains'].items())
        # pie_labels = [x[0] for x in pie_data]
        # pie_values = [x[-1] for x in pie_data]
        pie_chart = charts.Pie(self.json['report']['top_domains'])
        self.attach_png('top_domains_pie', pie_chart.bytes)

        todays_date = datetime.now().isoformat(timespec="hours").split("T")[0]
        self.subject = f'Credshed Scraping Report {todays_date}'


    @property
    def json(self):

        json = super().json

        unique = json['report']['total_unique_accounts']
        total = json['report']['total_accounts']

        header = f'{total:,} ACCOUNTS IN THE PAST {self.days:,} DAYS ({unique:,} NEVER-BEFORE-SEEN)'

        json.update({
            'header': header
        })
        return json