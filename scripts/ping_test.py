#!/usr/bin/env python

import urllib
import sys
import os
import MySQLdb
import subprocess

rows = {}

############## ping test ###########################

output = subprocess.Popen(['/bin/ping','-c', '5', 'www.sonic.net'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

for line in output[0].decode('utf-8').split('\n'):
   if "min/avg/max/mdev" in line:
      times = line.split('=')[1][:-3].split('/')
      rows['latency'] = times[1]

############## update database #####################

try:
    db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
    db.autocommit(True)

    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    for k,v in rows.items():
        #print('{} = {}'.format(k,v))
        query = "insert into netmon (parameter, value, timestamp) values ('{}', '{}', now())".format(k,v)
        cursor.execute(query)

    db.close()

except Exception as e:
    print('Error: ({})***'.format(e))

