#!/usr/bin/env python

# all the imports
import time
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app, jsonify
from wtforms import Form, StringField, validators, SubmitField, SelectField, BooleanField

log_pages = Blueprint('log', __name__, url_prefix='/log')

class LogForm(Form):
    day       = SelectField('day',  choices = ['None'], validators=[validators.DataRequired()])
    page      = SelectField('page', choices = [(str(i),str(i)) for i in range(1,101)], validators=[validators.DataRequired()])
    update    = SubmitField("update")
    ssid      = StringField('user_log.ssid',[validators.Length(min=0,max=20)])
    mac       = StringField('user_log.mac',[validators.Length(min=0,max=20)])
    ap_name   = StringField('user_log.ap_name',[validators.Length(min=0,max=20)])
    ap_mac    = StringField('user_log.ap_mac',[validators.Length(min=0,max=20)])
    name      = StringField('user_log.name',[validators.Length(min=0,max=20)])

@log_pages.route('/', methods=['GET', 'POST'])
def print_log():

    form = LogForm(request.form)

    days =[time.strftime("%Y-%m-%d",time.localtime(time.time()-(i*3600*24))) for i in range(0,30)]
    form.day.choices = [(day,day) for day in days]

    if request.method == 'POST' and form.validate():
        curr_date = form.day.data
        sel = "user_log.timestamp >= '%s 00:00:00' and user_log.timestamp <= '%s 23:59:59'" % (form.day.data,form.day.data)

        for f in form:
            if isinstance(f,StringField) and len(f.data) > 0:
                if f.name == 'mac':
                    sel += " and user_log.mac like '%%%s%%'" % (f.data)
                else:
                    sel += " and %s like '%%%s%%'" % (f.name,f.data)

        offset = 1000 * (int(form.page.data)-1)
    else:
        curr_date  = time.strftime("%Y-%m-%d",time.localtime())
        sel    = "user_log.timestamp >= current_date()"
        offset = 0

    items = []

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        query =  "select user_log.timestamp, user_log.ssid, user_log.mac, user_log.ap_mac, user_log.ap_name, user_log.name "
        query += "from user_log where " + sel + " order by user_log.timestamp desc limit %i,%i" % (offset,1000)

        cursor.execute(query)

        items = cursor.fetchall()

    except Exception as e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return render_template('log.html', curr_date=curr_date, form=form, items=items)

