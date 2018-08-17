#!/usr/bin/env python2

# all the imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app
from wtforms import Form, TextField, validators, SubmitField, SelectField, \
     BooleanField, FieldList, FormField, HiddenField

# Add relative path
import sys,os

SsidList = ['parish_staff', 'parish_user', 'parish_guest']

user_pages = Blueprint('users', __name__, url_prefix='/users')

class UserForm(Form):
    idx      = HiddenField('idx')
    user     = HiddenField('user')
    ssid     = HiddenField('ssid')
    password = TextField('password',[validators.Length(min=0,max=20)])
    notes    = TextField('notes',[validators.Length(min=0,max=100)])
    enable   = BooleanField('enable')
    delete   = BooleanField('delete')
    update   = SubmitField("update")

class UserAddForm(Form):
    user     = TextField('user',[validators.Length(min=0,max=20)])
    ssid     = HiddenField('ssid')
    password = TextField('password',[validators.Length(min=0,max=20)])
    notes    = TextField('notes',[validators.Length(min=0,max=100)])
    enable   = BooleanField('enable')
    add      = SubmitField("add")

@control_pages.route('/', methods=['GET'])
def print_users():
    ssids = {}

    for ssid in SsidList:
        ssids[ssid] = {'add' : ScheduleAddForm(), 'items' : [], 'name' : ssid}
        ssids[ssid]['add'].aform.data = ssid

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('users.html', ssids=ssids)

    for ssid in SsidList:
        cursor.execute("select user, ssid, passsword, notes, enable from users where 'ssid' = '{}'".format(ssid))
        ssids[ssid]['items'] = cursor.fetchall()

    return render_template('users.html', ssids=ssids)

@control_pages.route('/add', methods=['POST','GET'])
def add_user():

    aform = UserAddForm(request.form)

    if request.method == 'POST':
        user     = aform.user.data
        ssid     = aform.ssid.data
        password = aform.password.data
        notes    = aform.notes.data
        enable   = aform.enable.data

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("insert into `users` (`user`, `ssid`, `password`, 'notes', 'enable') VALUES ('{}', '{}', '{}', '{}', '{}')".format(user,ssid,password,notes,enable))

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))

    return redirect(url_for('.print_user'))

@control_pages.route('/edit', methods=['POST','GET'])
def edit_user():

    pForm = UserForm(request.form)
    user     = aform.user.data
    ssid     = aform.ssid.data
    password = aform.password.data
    notes    = aform.notes.data
    enable   = aform.enable.data
    delete   = aform.delete.data

    if postForm.delete.data:
        query = "delete from 'users' where 'user' = '{}'".format(user)

    else:
        query = "update 'users' set 'password' = '{}', 'notes' = '{}', 'enable' = '{}' where 'user' = '{}'".format(password,notes,enable,user)

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))

    return redirect(url_for('.print_users'))

