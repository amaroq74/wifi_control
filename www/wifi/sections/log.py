#!/usr/bin/env python2

# all the imports
import time
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app, jsonify
from wtforms import Form, TextField, validators, SubmitField, SelectField, BooleanField

log_pages = Blueprint('log', __name__, url_prefix='/log')

class LogForm(Form):
    day     = SelectField('day',   choices = ['None'], validators=[validators.Required()])
    page    = SelectField('page',  choices = [(str(i),str(i)) for i in range(1,101)], validators=[validators.Required()])
    update  = SubmitField("update")
    user    = TextField('user',[validators.Length(min=0,max=20)])
    ssid    = TextField('ssid',[validators.Length(min=0,max=20)])
    mac     = TextField('mac',[validators.Length(min=0,max=20)])
    ap      = TextField('ap',[validators.Length(min=0,max=20)])

def updateDays(form):
    days =[time.strftime("%Y-%m-%d",time.localtime(time.time()-(i*3600*24))) for i in range(0,30)]
    form.day.choices = [(day,day) for day in days]

def genSelect(method,form,table):
    perPage = 1000
    if method == 'POST' and form.validate():
        cdate = form.day.data
        sel = "timestamp >= '%s 00:00:00' and timestamp <= '%s 23:59:59'" % (form.day.data,form.day.data)

        for f in form:
            if isinstance(f,TextField) and len(f.data) > 0:
                sel += " and %s.%s like '%%%s%%'" % (table,f.name,f.data)

        offset = perPage * (int(form.page.data)-1)
    else:
        cdate  = time.strftime("%Y-%m-%d",time.localtime())
        sel    = "timestamp >= current_date()"
        offset = 0

    return cdate,sel,offset,perPage

@log_pages.route('/', methods=['GET', 'POST'])
def print_log():

    curr_date,sel,offset,count = genSelect(request.method,form,'user_log')
    form = SensorLogForm(request.form)
    updateDays(form)
    items = []

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("select timestamp, user, ssid, amc, ap from users where " + sel)
        items = cursor.fetchall()
        
    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))

    return render_template('log.html', curr_date=curr_date, form=form, items=items)

