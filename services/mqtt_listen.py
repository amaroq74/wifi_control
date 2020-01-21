#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import MySQLdb

ListenTopics = {'stat/fc/door2' : {'name':'East_Door', 'last':0 },
                'stat/fc/door1' : {'name':'West_Door', 'last':0 }}

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt server")
    for k,v in ListenTopics.items():
        client.subscribe(k)

def on_message(client, userdata, msg):
    try:
        door  = ListenTopics[msg.topic]['name']
        state   = 1 if str(msg.payload.decode('utf-8')) == 'Open' else 0
        changed = 0 if state == ListenTopics[msg.topic]['last'] else 1

        ListenTopics[msg.topic]['last'] = state

        db = MySQLdb.connect(host='127.0.0.1',user='network',passwd='network',db='network')
        db.autocommit(True)

        cursor = db.cursor(MySQLdb.cursors.DictCursor)

        query = f"insert into door_log (door, timestamp, state, changed) values ('{door}', now(), '{state}', '{changed}')"
        cursor.execute(query)
        db.close()

    except Exception as e:
        print('*** Got Error ({})***'.format(e))
        exit()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("saint.pius.org", 1883, 60)

client.loop_forever()

