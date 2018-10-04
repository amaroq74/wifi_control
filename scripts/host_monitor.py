#!/usr/bin/env python2

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText

sender   = 'root@pius.org'
receiver = 'ryan@pius.org'

hosts = [ 'core-sw-pc1',
          'core-sw-rc1',
          'core-sw-ch1',
          'core-sw-hc1',
          'core-sw-gy1',
          'core-ap-pc1',
          'core-ap-pc2',
          'core-ap-rc1',
          'core-ap-ch1',
          'core-ap-hc1',
          'core-ap-gy1',
          'sec-sw-pc1',
          'sec-sw-rc1',
          'sec-sw-ch1',
          'sec-sw-ch2',
          'sec-sw-hc1',
          'sec-sw-gy1',
          'sec-sw-sc1',
          'sec-sw-sc2',
          'sec-nvr',
          'sec-cam1',
          'sec-cam2',
          'sec-cam3',
          'sec-cam4',
          'sec-cam5',
          'sec-cam6',
          'sec-cam7',
          'sec-cam8',
          'sec-cam9',
          'sec-cam12',
          'sec-cam13',
          'sec-cam14',
          'sec-cam15',
          'sec-cam16',
          'sec-cam17',
          'sec-cam18',
          'sec-cam19',
          'sec-cam20',
          'sec-cam21']

missing = []

for host in hosts:
    resp = os.system('ping -c 1 ' + host)
    if resp != 0:
        missing.append(host)

if len(missing) > 0:

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Missing hosts detected'
    msg['From']    = sender
    msg['To']      = receiver

    text = "\n\nMissing hosts detected:\n\n"

    for miss in missing:
       text += miss + '\n'

    msg.attach(MIMEText(text, 'plain'))

    try:
       smtpObj = smtplib.SMTP('localhost')
       smtpObj.sendmail(sender, receiver, msg.as_string())
       print "Successfully sent email"
    except smtplib.SMTPException:
       print "Error: unable to send email"

