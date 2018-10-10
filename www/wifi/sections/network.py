#!/usr/bin/env python

# all the imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, Blueprint, current_app, make_response

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib 
import time
import StringIO
import MySQLdb

# Add relative path
import sys,os
sys.path.append(os.path.dirname(__file__) + "/../../pylib")

network_pages = Blueprint('network', __name__, url_prefix='/network')

# Dimenstions
DimX = 12
DimY = 4

# Convert time axis
def convert_time(rows):
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = -1.0 * (time.altzone if is_dst else time.timezone)

    return(matplotlib.dates.epoch2num([(float(row['utime']) + float(utc_offset)) for row in rows]))

def convert_load(rows):                                                                      
    return([row['avg'] if row['avg'] < 100.0 else 100.0 for row in rows])

# Generic plot function
def generic_plot ( title, leftLabel, leftData, rightLabel=None, rightData=None ):
    fig = Figure((DimX, DimY),100)
    canvas = FigureCanvas(fig)
    fig.suptitle(title)

    axesA = fig.add_subplot(111)
    axesA.tick_params(axis='both', which='major', labelsize='x-small')
    axesA.tick_params(axis='both', which='minor', labelsize='x-small')
    axesA.grid(True)
    axesA.set_ylabel(leftLabel,fontsize='x-small')

    axesA.set_xlabel('Time',fontsize='x-small')
    axesA.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))

    # Process left axis values
    for l in leftData:
        axesA.plot_date(l['xdata'],l['ydata'],l['line'],label=l['label'])

    # Second Axes
    if rightData:
        axesB = axesA.twinx()
        axesB.tick_params(axis='both', which='major', labelsize='x-small')
        axesB.tick_params(axis='both', which='minor', labelsize='x-small')
        axesB.grid(True)
        axesB.set_ylabel(rightLabel,fontsize='x-small')

        # Process right axis values
        for r in rightData:
            axesB.plot_date(r['xdata'],r['ydata'],r['line'],label=r['label'])

    output = StringIO.StringIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@network_pages.route('/plot/period/<int:period>')
@network_pages.route('/plot/day/<day>')
def plot_network(period=None,day=None):

    try:
        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        query =  "select UNIX_TIMESTAMP(timestamp) as utime, avg, timestamp from latency where timestamp > (now() - interval 24 hour) order by timestamp desc"
        cursor.execute(query)
        items = cursor.fetchall()

    except Exception, e:
        print('*** Failed to connect to database ({})***'.format(e))
        return render_template('error.html', error=str(e))

    data = [{'xdata':convert_time(items),
             'ydata':convert_load(items),
             'line':'b-',
             'label':'Day'}]

    return(generic_plot ( 'Latency / Downtime', 'mS', data ))

@network_pages.route('/')
@network_pages.route('/period/<int:period>')
@network_pages.route('/day/<day>')
def network(period=None, day=None):

    if period:
        args = '/wifi/network/plot/period/%i' %(period)
    elif day:
        args = '/wifi/network/plot/day/%s' %(day)
    else:
        args = '/wifi/network/plot/period/24'

    net = []
    net.append(args)

    return render_template('network.html', net=net)

