#!/usr/bin/python

import requests
import logging
import random
import time

RESTFUL_HOST="localhost"
RESTFUL_PORT=6001

def sendAction(objectName, payload):
	global RESTFUL_HOST
	global RESTFUL_PORT
	
	url = 'http://{}:{}/api/{}/actions'.format(RESTFUL_HOST, RESTFUL_PORT, objectName)
	logging.warn('Calling {} with payload {}'.format(url, payload))
	requests.post(url, json=payload)

def spinPlayer(amount):
	if amount < 0:
		actionType = "turn-left"
		amount = abs(amount)
	else:
		actionType = "turn-right"
	
	sendAction('player', {'type': actionType, 'amount': amount})

while 1 == 1:
	spinAmount = int((random.random() * 200.0) - 100)
	spinPlayer(spinAmount)
	time.sleep(5)
