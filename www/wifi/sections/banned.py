#!/usr/bin/env python2

# all the imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app
from wtforms import Form, TextField, validators, SubmitField, SelectField, \
     BooleanField, FieldList, FormField, HiddenField

# Add relative path
import sys,os

SsidList = ['parish_staff', 'parish_user', 'parish_guest']

banned_pages = Blueprint('banned', __name__, url_prefix='/banned')

class BanDelForm(Form):
    idx      = HiddenField('idx')
    mac      = HiddenField('mac')
    ssid     = HiddenField('ssid')
    delete   = SubmitField("delete")

class BanAddForm(Form):
    mac      = TextField('mac',[validators.Length(min=0,max=20)])
    ssid     = TextField('ssid',[validators.Length(min=0,max=20)])
    add      = SubmitField("add")

@control_pages.route('/', methods=['GET'])
def print_banned():
    ssids = {}

    for ssid in SsidList:
        ssids[ssid] = {'add' : BanAddForm(), 'items' : [], 'name' : ssid}
        ssids[ssid]['add'].aform.data = ssid

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('banned.html', ssids=ssids)

    for ssid in SsidList:
        cursor.execute("select mac, ssid from banned where 'ssid' = '{}'".format(ssid))
        ssids[ssid]['items'] = cursor.fetchall()

    return render_template('banned.html', ssids=ssids)

@control_pages.route('/add', methods=['POST','GET'])
def add_user():

    aform = BanAddForm(request.form)

    if request.method == 'POST':
        mac      = aform.mac.data
        ssid     = aform.ssid.data

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("insert into `banned` (`mac`, `ssid`) VALUES ('{}', '{}')".format(mac,ssid))

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))

    return redirect(url_for('.print_banned'))

@control_pages.route('/del', methods=['POST','GET'])
def del_user():

    pForm = UserDelForm(request.form)
    idx      = aform.idx.data
    mac      = aform.user.data
    ssid     = aform.ssid.data

    query = "delete from 'banned' where 'idx' = '{}'".format(idx)

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))

    return redirect(url_for('.print_banned'))

