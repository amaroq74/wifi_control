#!/usr/bin/env python2

# all the imports
import time
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app, jsonify
from wtforms import Form, TextField, validators, SubmitField, SelectField, BooleanField

hosts_pages = Blueprint('hosts', __name__, url_prefix='/hosts')

class HostForm(Form):
    update  = SubmitField("update")
    mac     = TextField('dhcp_hosts.mac',[validators.Length(min=0,max=20)])
    name    = TextField('dhcp_hosts.name',[validators.Length(min=0,max=20)])
    ip      = TextField('dhcp_hosts.ip',[validators.Length(min=0,max=20)])
    user    = TextField('ap_hosts.user',[validators.Length(min=0,max=20)])
    ssid    = TextField('ap_hosts.ssid',[validators.Length(min=0,max=20)])
    ap_name = TextField('ap_hosts.ap_name',[validators.Length(min=0,max=20)])

@hosts_pages.route('/', methods=['GET', 'POST'])
def print_hosts():

    form = HostForm(request.form)
    sel = ""

    if request.method == 'POST' and form.validate():
        pre = " "
        for f in form:
            if isinstance(f,TextField) and len(f.data) > 0:
                if f.name == 'mac':
                    sel += " and user_log.mac like '%%%s%%'" % (f.data)
                elif f.data == "None":
                    sel += pre + "%s is NULL" % (f.name)
                else:
                    sel += pre + "%s like '%%%s%%'" % (f.name,f.data)
                pre = " and "

    items = []

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        query =  "select dhcp_hosts.last, dhcp_hosts.mac, dhcp_hosts.name, dhcp_hosts.ip, "
        query += "ap_hosts.ssid, ap_hosts.user, ap_hosts.ap_name "
        query += "from dhcp_hosts left join ap_hosts on ap_hosts.mac = dhcp_hosts.mac "

	if sel != "":
            query += "where " + sel + " "

        query += "order by dhcp_hosts.last desc"

        cursor.execute(query)

        items = cursor.fetchall()

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return render_template('hosts.html', form=form, items=items)

