#!/usr/bin/env python

import urllib
import sys
import os
import MySQLdb
import subprocess

############## get modem stats ###########################

Params = {
    'Cum. Sec. w/Severe Errors' : 'cum_sec_sev_err',
    'DSL Training Errors'       : 'dsl_train_errs',
    'Link Retrains'             : 'link_retrains',
    'Loss of Margin Failures'   : 'loss_mar_fails',
    'Training Timeouts'         : 'train_touts',
    'Uncorrectable Blocks'      : 'uncorr_blocks',
    'Loss of Signal Failures'   : 'loss_sig_fails',
    'DSL Unavailable Seconds'   : 'dsl_unavail_sec',
    'Cum. Seconds w/Errors'     : 'cum_sec_errs',
    'Corrected Blocks'          : 'corr_blocks',
    'Loss of Framing Failures'  : 'loss_frame_fails',
    'Loss of Power Failures'    : 'loss_pwr_fails'}

fh = urllib.urlopen("http://192.168.1.254/xslt?PAGE=C_1_0")
ures = fh.read().strip()
fh.close()

collect = False
title = None
row = None
val = ''
rows = {}

for line in ures.split('\n'):
    l = line.strip()

    if l == '<h2>DSL Link Errors</h2>':
        collect = True
    elif collect:
        if l == "<tr>":
            title = None
            row   = []
        elif l == "</tr>":
            if title in Params:
                nt = Params[title]
                rows[nt + '_tot'] = row[0]
                rows[nt + '_24h'] = row[1]
                rows[nt + '_15m'] = row[2]
            row = None

        elif row is not None and l[0:4] == '<td>':
            val = l[4:-5]

            if title is None:
                title = val
            else:
                row.append(val)

############## ping test ###########################

output = subprocess.Popen(['/bin/ping','-c', '5', 'www.sonic.net'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

for line in output[0].split('\n'):
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

except Exception, e:
    print('Error: ({})***'.format(e))

