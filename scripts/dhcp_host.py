#!/usr/bin/env python2

import sys

if len(sys.argv) < 2:
    exit()

cmd = sys.argv[1]
mac = sys.argv[2]
ip  = sys.argv[3]
name = "Unknown"

if len(sys.argv) > 4:
    name = sys.argv[4]

if cmd == 'del':
    exit()

import MySQLdb
try:
    db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
    db.autocommit(True)

except Exception, e:
    print('*** Failed to connect to database ({})***'.format(e))
    exit()

cursor = db.cursor(MySQLdb.cursors.DictCursor)

print("cmd={}, mac={}, ip={}, name={}".format(cmd,mac,ip,name))

query = "replace into hosts (mac, ip, name) values ('{}', '{}', '{}')".format(mac,ip,name)
cursor.execute(query)

db.close()

