#!/usr/bin/env python2

# all the imports
import time
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app, jsonify
from wtforms import Form, TextField, validators, SubmitField, SelectField, BooleanField

log_pages = Blueprint('log', __name__, url_prefix='/log')

class LogForm(Form):
    day       = SelectField('day',  choices = ['None'], validators=[validators.Required()])
    page      = SelectField('page', choices = [(str(i),str(i)) for i in range(1,101)], validators=[validators.Required()])
    update    = SubmitField("update")
    user      = TextField('user_log.user',[validators.Length(min=0,max=20)])
    ssid      = TextField('user_log.ssid',[validators.Length(min=0,max=20)])
    mac       = TextField('user_log.mac',[validators.Length(min=0,max=20)])
    ap_name   = TextField('user_log.ap_name',[validators.Length(min=0,max=20)])
    ap_mac    = TextField('user_log.ap_mac',[validators.Length(min=0,max=20)])
    name      = TextField('dhcp_hosts.name',[validators.Length(min=0,max=20)])
    duplicate = BooleanField('user_log.duplicate')

@log_pages.route('/', methods=['GET', 'POST'])
def print_log():

    form = LogForm(request.form)

    days =[time.strftime("%Y-%m-%d",time.localtime(time.time()-(i*3600*24))) for i in range(0,30)]
    form.day.choices = [(day,day) for day in days]

    if request.method == 'POST' and form.validate():
        curr_date = form.day.data
        sel = "user_log.timestamp >= '%s 00:00:00' and user_log.timestamp <= '%s 23:59:59'" % (form.day.data,form.day.data)

        if not form.duplicate.data: sel += " and user_log.duplicate = '0'"

        for f in form:
            if isinstance(f,TextField) and len(f.data) > 0:
                if f.name == 'mac':
                    sel += " and user_log.mac like '%%%s%%'" % (f.data)
                elif f.name != 'duplicate':
                    sel += " and %s like '%%%s%%'" % (f.name,f.data)

        offset = 1000 * (int(form.page.data)-1)
    else:
        curr_date  = time.strftime("%Y-%m-%d",time.localtime())
        sel    = "user_log.timestamp >= current_date() and user_log.duplicate = '0'"
        offset = 0

    items = []

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        query =  "select user_log.timestamp, user_log.user, user_log.ssid, user_log.mac, user_log.ap_mac, user_log.ap_name, dhcp_hosts.name, user_log.duplicate "
        query += "from user_log left join dhcp_hosts on dhcp_hosts.mac = user_log.mac "
        query += "where " + sel + " order by user_log.timestamp desc limit %i,%i" % (offset,1000)

        cursor.execute(query)

        items = cursor.fetchall()

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return render_template('log.html', curr_date=curr_date, form=form, items=items)

