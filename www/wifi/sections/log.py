#!/usr/bin/env python2

# all the imports
import time
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app, jsonify
from wtforms import Form, TextField, validators, SubmitField, SelectField, BooleanField

log_pages = Blueprint('log', __name__, url_prefix='/log')

class LogForm(Form):
    day     = SelectField('day',  choices = ['None'], validators=[validators.Required()])
    page    = SelectField('page', choices = [(str(i),str(i)) for i in range(1,101)], validators=[validators.Required()])
    update  = SubmitField("update")
    user    = TextField('user',[validators.Length(min=0,max=20)])
    ssid    = TextField('ssid',[validators.Length(min=0,max=20)])
    mac     = TextField('mac',[validators.Length(min=0,max=20)])
    ap      = TextField('ap',[validators.Length(min=0,max=20)])
    host    = TextField('host',[validators.Length(min=0,max=20)])

@log_pages.route('/', methods=['GET', 'POST'])
def print_log():

    form = LogForm(request.form)

    days =[time.strftime("%Y-%m-%d",time.localtime(time.time()-(i*3600*24))) for i in range(0,30)]
    form.day.choices = [(day,day) for day in days]

    if request.method == 'POST' and form.validate():
        curr_date = form.day.data
        sel = "timestamp >= '%s 00:00:00' and timestamp <= '%s 23:59:59'" % (form.day.data,form.day.data)

        for f in form:
            if isinstance(f,TextField) and len(f.data) > 0:
                sel += " and %s like '%%%s%%'" % (f.name,f.data)

        offset = 1000 * (int(form.page.data)-1)
    else:
        curr_date  = time.strftime("%Y-%m-%d",time.localtime())
        sel    = "timestamp >= current_date()"
        offset = 0

    items = []

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("select timestamp, user, ssid, mac, ap from user_log where " + sel + " order by timestamp desc limit %i,%i" % (offset,1000))

        items = cursor.fetchall()

        # Get hostnames       
	for it in items:
            key = it['mac'].replace('-',':')
            cursor.execute("select mac, name from hosts where mac='{}'".format(key))
            res = cursor.fetchone()
            if res is None:
                it['host']='Unknown'
            else:
                it['host']= res['name']
 
    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return render_template('log.html', curr_date=curr_date, form=form, items=items)

