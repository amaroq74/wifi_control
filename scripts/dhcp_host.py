#!/usr/bin/env python2

import sys
import os

if len(sys.argv) < 2 or sys.argv[1] == 'del':
    exit()

mac   = sys.argv[2].replace(':','-')
ip    = sys.argv[3]
name  = "Unknown"
iface = "Unknown"

if len(sys.argv) > 4:
    name = sys.argv[4]

if 'DNSMASQ_INTERFACE' in os.environ:
    iface = os.environ['DNSMASQ_INTERFACE']

import MySQLdb
try:
    db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
    db.autocommit(True)

except Exception, e:
    print('*** Failed to connect to database ({})***'.format(e))
    exit()

cursor = db.cursor(MySQLdb.cursors.DictCursor)

query = "replace into dhcp_hosts (mac, ip, name, interface, last) values ('{}', '{}', '{}', '{}', now())".format(mac,ip,name,iface)
cursor.execute(query)

db.close()

