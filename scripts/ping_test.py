#!/usr/bin/env python2

import sys
import os
import MySQLdb
import subprocess

host="www.sonic.net"

pmin = 0
pavg = 0
pmax = 0

output = subprocess.Popen(['/bin/ping','-c', '5', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

for line in output[0].split('\n'):
   if "min/avg/max/mdev" in line:
      times = line.split('=')[1][:-3].split('/')
      pmin = times[0]
      pavg = times[1]
      pmax = times[2]

try:
    db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
    db.autocommit(True)

    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    query = "insert into latency (host, min, max, avg, timestamp) values ('{}', '{}', '{}', '{}', now())".format(host,pmin,pmax,pavg)
    cursor.execute(query)

    db.close()

except Exception, e:
    print('Error: ({})***'.format(e))

