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

banned_pages = Blueprint('banned', __name__, url_prefix='/banned')

class BanDelForm(Form):
    idx      = HiddenField('idx')
    mac      = HiddenField('mac')
    ssid     = HiddenField('ssid')
    notes    = HiddenField('notes')
    delete   = SubmitField("delete")

class BanAddForm(Form):
    mac      = StringField('mac',[validators.Length(min=0,max=20)])
    ssid     = HiddenField('ssid')
    notes    = StringField('notes',[validators.Length(min=0,max=100)])
    add      = SubmitField("add")

@banned_pages.route('/', methods=['GET'])
def print_banned():
    ssids = []

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        for ssid in SsidList:
            ent = {'add' : BanAddForm(), 'forms' : [], 'name' : ssid}
            ent['add'].ssid.data = ssid

            cursor.execute("select id, mac, ssid, notes from banned where ssid = '{}' order by mac".format(ssid))
            rows = cursor.fetchall()

            for row in rows:
                ent['forms'].append(BanDelForm( idx   = row['id'],
                                                mac   = row['mac'],
                                                notes = row['notes'],
                                                ssid  = row['ssid']))

            ssids.append(ent)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return render_template('banned.html', ssids=ssids)

@banned_pages.route('/add', methods=['POST','GET'])
def add_banned():

    aForm = BanAddForm(request.form)

    if request.method == 'POST':
        mac   = aForm.mac.data
        ssid  = aForm.ssid.data
        notes = aForm.notes.data

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("insert into banned (mac, ssid, notes) VALUES ('{}', '{}', '{}')".format(mac,ssid,MySQLdb.escape_string(notes)))

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return redirect(url_for('.print_banned'))

@banned_pages.route('/del', methods=['POST','GET'])
def del_banned():

    pForm = BanDelForm(request.form)
    idx   = pForm.idx.data
    mac   = pForm.mac.data
    ssid  = pForm.ssid.data
    notes = pForm.notes.data

    query = "delete from banned where id = '{}'".format(idx)

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    return redirect(url_for('.print_banned'))

