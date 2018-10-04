#!/usr/bin/env python2

import MySQLdb
import time

RLM_MODULE_REJECT = 0
RLM_MODULE_FAIL = 1
RLM_MODULE_OK = 2
RLM_MODULE_HANDLED = 3
RLM_MODULE_INVALID = 4
RLM_MODULE_USERLOCK = 5
RLM_MODULE_NOTFOUND = 6
RLM_MODULE_NOOP = 7
RLM_MODULE_UPDATED = 8
RLM_MODULE_NUMCODES = 9

# from radiusd.h
L_DBG = 1
L_AUTH = 2
L_INFO = 3
L_ERR = 4
L_PROXY = 5
L_CONS = 128

ApAlias = {
   '4e-26-af-53-5e' : 'gym1',
   '4e-26-af-53-5f' : 'gym1 5G',
   '84-c6-08-d1-7c' : 'homer1',
   '84-c6-08-d1-7d' : 'homer1 5G',
   '84-c6-08-d6-4a' : 'pcenter1',
   '84-c6-08-d6-4b' : 'pcenter1 5G',
   '84-c6-08-e6-f8' : 'pcenter2',
   '84-c6-08-e6-f9' : 'pcenter2 5G',
   '84-c6-08-df-6a' : 'church1',
   '84-c6-08-df-6b' : 'church1 5G',
   '84-c6-08-e2-e4' : 'rectory1',
   '84-c6-08-e2-e5' : 'rectory1 5G'
}

lastLog = { 'time'   : time.time(),
            'user'   : None,
            'mac'    : None,
            'ssid'   : None,
            'ap_mac' : None }

def instantiate(p):
    return 0

def authorize(p):
    d = dict(p)

    print('*** authorize called ***')
    print(d)

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return RLM_MODULE_REJECT

    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    # Lookup user
    user  = d['User-Name'].strip('"')

    # Find user
    cursor.execute("select password,ssid,enable from users where user='{}'".format(user))
    row = cursor.fetchone()

    # Entry not found
    if row is None:
        db.close()
        print('*** User {} not found ***'.format(user))
        return RLM_MODULE_REJECT

    # User is disabled
    elif row['enable'] != 1:
        db.close()
        print('*** User {} is disabled ***'.format(user))
        return RLM_MODULE_REJECT

    # Entry found
    else:
        print('*** Found user {} ***'.format(user))
        pword = row['password']
        ssid  = row['ssid']

    # Format reply
    reply = ( ('Reply-Message', 'Welcome'), )
    config = ( ('Cleartext-Password', pword), )

    # Passed info does not contain station information
    if not ('Called-Station-Id' in d and 'Calling-Station-Id' in d):
        db.close()
        print('*** Return ok for short session ***')
        return (RLM_MODULE_OK, reply, config)

    # Format SSID
    raw_ssid = d['Called-Station-Id'].strip('"').split(':')[1]

    # Drop ssid suffix
    if raw_ssid.endswith('_5G'):
        req_ssid = raw_ssid[:-len('_5G')]
    else:
        req_ssid = raw_ssid

    # SSID does not match
    if ssid != req_ssid:
        db.close()
        print('*** Wrong ssid ***')
        return RLM_MODULE_REJECT

    # Check if mac is banned
    mac = d['Calling-Station-Id'].strip('"').lower()
    cursor.execute("select id from banned where mac='{}' and ssid='{}'".format(mac,ssid))
    if cursor.fetchone() is not None:
        print('*** mac is banned ***')
        db.close()
        return RLM_MODULE_REJECT

    # Lookup access point, first and last bytes seem to be dynamic in AP
    ap_mac = d['Called-Station-Id'].strip('"').split(':')[0].lower()
    ap_short = ap_mac[3:]
    ap_name  = ap_mac

    # Look for AP alias
    if ap_short in ApAlias:
        ap_name = ApAlias[ap_short]

    # Insert into hosts table
    cursor.execute("replace into ap_hosts (mac, ssid, user, ap_name, ap_mac, last) values ('{}', '{}', '{}', '{}', '{}', now())".format(mac,raw_ssid,user,ap_name,ap_mac))

    # Filter duplicate log entries
    if (lastLog['user'] == user) and (lastLog['mac'] == mac) and (lastLog['ssid'] == raw_ssid) and (lastLog['ap_mac'] == ap_mac): dup = 1 
    else: dup = 0

    lastLog['user']   = user 
    lastLog['mac']    = mac 
    lastLog['ssid']   = raw_ssid
    lastLog['ap_mac'] = ap_mac

    # Log entry
    cursor.execute("insert into user_log (user, ssid, mac, ap_mac, ap_name, duplicate) VALUES ('{}', '{}', '{}', '{}', '{}', '{}' )".format(user,raw_ssid,mac,ap_mac,ap_name,dup))

    db.close()
    return (RLM_MODULE_OK, reply, config)

