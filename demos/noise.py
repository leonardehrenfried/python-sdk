#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script using the Wunderbar over the Relayr cloud.

This will connect to a microphone, read its noise level and send
an email notification to some receiver if that noise level exceeds
a certain threshold.
"""

import sys
import json
import time
import getpass
import smtplib
from email.mime.text import MIMEText

from relayr import Client


# Replace with your own values!
ACCESS_TOKEN = '...'
MICROPHONE_ID = '...'
# EMAIL/SMTP settings, please provide your own!
RECEIVER = '...'
SMTP_SERVER = '...'
SMTP_USERNAME = '...'
SMTP_PASSWORD = '' # will be requested at run time if left empty 

try:
    settings = [ACCESS_TOKEN, MICROPHONE_ID, RECEIVER, SMTP_SERVER, SMTP_USERNAME]
    assert not any(map(lambda x: x=='...', settings))
except AssertionError:
    print('Please provide meaningful settings in the code first!')
    sys.exit(1)


class Callbacks(object):
    "A class providing callbacks for incoming data from some device."

    def __init__(self, device):
        "An initializer to capture the device for later use."

        self.device = device

    def send_email(self, text):
        "Send an email notification."
        
        sender = 'Wunderbar <notification-noreply@relayr.io>'
        subject = 'Wunderbar Notification from Device: %s' % self.device.name
        msg = MIMEText(text)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = RECEIVER
        s = smtplib.SMTP(SMTP_SERVER)
        prompt = "SMTP user password for user '%s'? " % SMTP_USERNAME
        global SMTP_PASSWORD
        SMTP_PASSWORD = SMTP_PASSWORD or getpass.getpass(prompt)
        s.login(SMTP_USERNAME, SMTP_PASSWORD)
        s.sendmail(sender, [RECEIVER], msg.as_string())
        s.quit()
        print("Email notification sent to '%s'" % RECEIVER)

    def microphone(self, message, channel):
        "Callback displaying incoming noise level data and email if desired."

        # Needs workaround handling a Pubnub strangeness on Python 3...
        # not added here for brevity (see relayr/utils/workarounds.py).
        level = json.loads(message)['snd_level'] 

        print(level)
        threshold = 75
        if level > threshold:
            dname, did = self.device.name, self.device.id
            text = "Notification from '%s' (%s):\n" % (dname, did)
            text += ("The noise level now is %d (> %d)! " % (level, threshold))
            text += "Put on a sound protection helmet before you get deaf!"
            self.send_email(text)


def connect():
    "Connect to a device and read data for some time."

    c = Client(token=ACCESS_TOKEN)
    m = c.get_device(id=MICROPHONE_ID).get_info()
    cb = Callbacks(m)
    user = c.get_user()
    conn = user.connect_device(m, cb.microphone)
    conn.start()
    print("Monitoring '%s' (%s) for 60 seconds..." % (m.name, m.id))
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        print('')
    conn.stop()
    print("Stopped")


if __name__ == "__main__":
    connect()
