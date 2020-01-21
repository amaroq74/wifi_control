#!/usr/bin/env python3

import paho.mqtt.client as mqtt

client = mqtt.Client()

client.connect("saint.pius.org", 1883, 60)

client.loop_start()

def setOpen(chan):
    client.publish(f'stat/fc/{chan}', 'Open')

def setClosed(chan):
    client.publish(f'stat/fc/{chan}', 'Closed')

