#!/usr/bin/env python2

import MySQLdb
try:
   db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
   db.autocommit(True)

except Exception, e:
   print('*** Failed to connect to database ({})***'.format(e))
   exit()

cursor = db.cursor(MySQLdb.cursors.DictCursor)

user = 'ryan_staff'

# Find users
#cursor.execute("select * from users")
cursor.execute("select password,ssid,enable from users where user='{}'".format(user))
rows = cursor.fetchall()

for row in rows:
    print row

db.close()

