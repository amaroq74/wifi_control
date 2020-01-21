#!/usr/bin/env python3

import sys
import os

import MySQLdb
try:
    db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
    db.autocommit(True)

except Exception as e:
    print('*** Failed to connect to database ({})***'.format(e))
    exit()

cursor = db.cursor(MySQLdb.cursors.DictCursor)

query = "delete from netmon where timestamp < (now() - interval 60 day)"
cursor.execute(query)

query = "delete from user_log where timestamp < (now() - interval 60 day)"
cursor.execute(query)

query = "delete from dhcp_hosts where last < (now() - interval 60 day)"
cursor.execute(query)

query = "delete from ap_hosts where last < (now() - interval 60 day)"
cursor.execute(query)

db.close()

