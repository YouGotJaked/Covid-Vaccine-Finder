import json
from pathlib import Path
from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_JSON = Path(Path(__file__).parent.parent.parent, 'data', 'json',
                  'email.json')

try:
    with open(EMAIL_JSON) as json_file:
        CREDS = json.load(json_file)
except FileNotFoundError:
    raise('File {} not found.'.format(EMAIL_JSON))

def send_msg(message, recipient):
    try:
        server = SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(CREDS['sender'], CREDS['sender_password'])
    except SMTPException:
        raise('Could not connect to SMPT server with supplied credentials.')

    msg = MIMEMultipart()
    msg['From'] = CREDS['sender']
    msg['To'] = recipient
    msg['Subject'] = 'Covid Vaccine Finder'
    msg.attach(MIMEText(message, 'plain'))
    sms = msg.as_string()

    server.sendmail(CREDS['sender'], recipient, sms)
    server.quit()

def text(message):
    send_msg(message, CREDS['recipient_text'])

def email(message):
    send_msg(message, CREDS['recipient_email'])
