#!/usr/bin/env python

# all the imports
import time
import MySQLdb
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app, jsonify
from wtforms import Form, TextField, validators, SubmitField, SelectField, BooleanField

doors_pages = Blueprint('doors', __name__, url_prefix='/doors')

class LogForm(Form):
    day       = SelectField('day',  choices = ['None'], validators=[validators.Required()])
    page      = SelectField('page', choices = [(str(i),str(i)) for i in range(1,101)], validators=[validators.Required()])
    update    = SubmitField("update")
    door      = TextField('door_log.door', [validators.Length(min=0,max=20)])
    state     = TextField('door_log.state',[validators.Length(min=0,max=5)])
    changed   = BooleanField('udoorlog.changed')

@doors_pages.route('/', methods=['GET', 'POST'])
def print_log():

    form = LogForm(request.form)

    days =[time.strftime("%Y-%m-%d",time.localtime(time.time()-(i*3600*24))) for i in range(0,30)]
    form.day.choices = [(day,day) for day in days]

    if request.method == 'POST' and form.validate():
        curr_date = form.day.data
        sel = "door_log.timestamp >= '%s 00:00:00' and door_log.timestamp <= '%s 23:59:59'" % (form.day.data,form.day.data)

        if form.changed.data: sel += " and door_log.changed = '1'"

        for f in form:
            if isinstance(f,TextField) and len(f.data) > 0:
                if f.name != 'changed':
                    sel += " and %s like '%%%s%%'" % (f.name,f.data)

        offset = 1000 * (int(form.page.data)-1)
    else:
        curr_date  = time.strftime("%Y-%m-%d",time.localtime())
        sel    = "door_log.timestamp >= current_date() and door_log.changed = '1'"
        offset = 0

    items = []

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        query =  "select door_log.timestamp, door_log.door, door_log.changed, door_log.state "
        query += "from door_log "
        query += "where " + sel + " order by door_log.timestamp desc limit %i,%i" % (offset,1000)

        cursor.execute(query)

        items = cursor.fetchall()

    except Exception as e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return render_template('doors.html', curr_date=curr_date, form=form, items=items)

