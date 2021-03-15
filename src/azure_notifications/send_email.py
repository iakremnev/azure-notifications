import email
import smtplib
import sys

import azure_notifications.config

with open(sys.argv[1]) as f:
    msg = email.message_from_file(f)

s = smtplib.SMTP("localhost", azure_notifications.config.SMTP_SERVER_PORT)

s.send_message(msg)
s.quit()