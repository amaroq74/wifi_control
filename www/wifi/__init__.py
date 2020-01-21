#!/usr/bin/env python

# all the imports
from flask import Flask, url_for, request, redirect, render_template, session
from wtforms import Form, TextField, SubmitField, validators

from .sections.users   import user_pages
from .sections.banned  import banned_pages
from .sections.log     import log_pages
from .sections.hosts   import hosts_pages
from .sections.network import network_pages
from .sections.doors   import doors_pages

# configuration
SESSION_TYPE = 'memcached'
DEBUG = True
#SECRET_KEY = 'development key'

# Create application
app = Flask(__name__)
app.config.from_object(__name__)
app.register_blueprint(user_pages)
app.register_blueprint(banned_pages)
app.register_blueprint(log_pages)
app.register_blueprint(hosts_pages)
app.register_blueprint(network_pages)
app.register_blueprint(doors_pages)
app.secret_key = 'F77skFLsjkdsf\\][][)()0#$?KT'

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/')
@app.route('/index')
@app.route('/index.php')
def index():
    return app.send_static_file('index.html')

@app.route('/menu')
def menu():
    return app.send_static_file('menu.html')

