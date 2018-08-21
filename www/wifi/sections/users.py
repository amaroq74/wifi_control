#!/usr/bin/env python2

# all the imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app
from wtforms import Form, StringField, validators, SubmitField, SelectField, \
     BooleanField, FieldList, FormField, HiddenField

# Add relative path
import sys,os
import MySQLdb

SsidList = ['parish_staff', 'parish_user', 'parish_guest']

user_pages = Blueprint('users', __name__, url_prefix='/users')

class UserForm(Form):
    idx      = HiddenField('idx')
    user     = HiddenField('user')
    ssid     = HiddenField('ssid')
    pword    = StringField('pword', [validators.Length(min=0,max=50)])
    notes    = StringField('notes',[validators.Length(min=0,max=100)])
    enable   = BooleanField('enable')
    delete   = BooleanField('delete')
    update   = SubmitField("update")

class UserAddForm(Form):
    user     = StringField('user',[validators.Length(min=0,max=50)])
    ssid     = HiddenField('ssid')
    pword    = StringField('pword',[validators.Length(min=0,max=50)])
    notes    = StringField('notes',[validators.Length(min=0,max=100)])
    enable   = BooleanField('enable')
    add      = SubmitField("add")

@user_pages.route('/', methods=['GET'])
def print_users():
    ssids = []

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        for ssid in SsidList:
            ent = {'add' : UserAddForm(), 'forms' : [], 'name' : ssid}
            ent['add'].ssid.data = ssid
            ent['add'].enable.data = 1

            cursor.execute("select id, user, ssid, password, notes, enable from users where ssid = '{}' order by user".format(ssid))
            rows = cursor.fetchall()

            for row in rows:
                ent['forms'].append(UserForm( idx      = row['id'],
                                              user     = row['user'],
                                              ssid     = row['ssid'],
                                              pword    = row['password'],
                                              notes    = row['notes'],
                                              enable   = row['enable']))

            ssids.append(ent)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return render_template('users.html', ssids=ssids)

@user_pages.route('/add', methods=['POST','GET'])
def add_user():

    aForm = UserAddForm(request.form)

    if request.method == 'POST':
        user     = aForm.user.data
        ssid     = aForm.ssid.data
        pword    = aForm.pword.data
        notes    = aForm.notes.data
        enable   = 1 if aForm.enable.data else 0

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("insert into users (user, ssid, password, notes, enable) VALUES ('{}', '{}', '{}', '{}', '{}')".format(user,ssid,pword,MySQLdb.escape_string(notes),enable))

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return redirect(url_for('.print_users'))

@user_pages.route('/edit', methods=['POST','GET'])
def edit_user():

    pForm = UserForm(request.form)
    user     = pForm.user.data
    ssid     = pForm.ssid.data
    pword    = pForm.pword.data
    notes    = pForm.notes.data
    enable   = 1 if pForm.enable.data else 0
    delete   = pForm.delete.data
    idx      = pForm.idx.data

    if delete:
        query = "delete from users where id = '{}'".format(idx)

    else:
        query = "update users set password = '{}', notes = '{}', enable = '{}' where id = '{}'".format(pword,MySQLdb.escape_string(notes),enable,idx)

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return redirect(url_for('.print_users'))

