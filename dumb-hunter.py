#!/usr/bin/python

import requests
import logging
import random
import time
import json
import math

RESTFUL_HOST="localhost"
RESTFUL_PORT=6001

def sendAction(objectName, payload):
	global RESTFUL_HOST
	global RESTFUL_PORT
	
	url = 'http://{}:{}/api/{}/actions'.format(RESTFUL_HOST, RESTFUL_PORT, objectName)
	logging.debug('Calling {} with payload {}'.format(url, payload))
	try:
		requests.post(url, json=payload)
		return True
	except:
		logging.error('POST API call failed')
		return False
		
def getAction(objectName):
	global RESTFUL_HOST
	global RESTFUL_PORT
	
	url = 'http://{}:{}/api/{}'.format(RESTFUL_HOST, RESTFUL_PORT, objectName)
	logging.debug('Calling {}'.format(url))
	try:
		req = requests.get(url)
		data = json.loads(req.text)
		return data
	except:
		logging.error('GET API call failed')
		return None

def spinPlayer(amount):
	if amount < 0:
		actionType = "turn-left"
		amount = abs(amount)
	else:
		actionType = "turn-right"
	
	sendAction('player', {'type': actionType, 'amount': amount})

def movePlayer(amount):
	if amount < 0:
		actionType = "backward"
		amount = abs(amount)
	else:
		actionType = "forward"
	
	sendAction('player', {'type': actionType, 'amount': amount})

def shoot():
	sendAction('player', {'type': 'shoot'})


def distanceBetweenPoints(x1, y1, x2, y2):  
	dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
	return dist


def moveToPoint(destX, destY, attempts=20, pause=1, accuracy=25):
	"""Try to move in a straight line from where we are to a destination
	point in a finite amount of steps. Z axis is disregarded
	"""
	
	for i in range(attempts):
		currentData = getAction('player')
		logging.debug('moveToPoint iteration {} - I am at {} x {} @ {} deg, I need to get to {} x {}'.format(
			i,
			currentData["position"]["x"],
			currentData["position"]["y"],
			currentData["angle"],
			destX,
			destY
		))
		
		distance = distanceBetweenPoints(
			currentData["position"]["x"],
			currentData["position"]["y"],
			destX,
			destY
		)
		
		if abs(distance) < accuracy:
			logging.debug('moveToPoint is close enough - {} x {} vs {} x {}'.format(
				currentData["position"]["x"],
				currentData["position"]["y"],
				destX,
				destY
			))
			return True
		
		
		
		time.sleep(pause)
	
	return False
	


def findNearestEnemy():
	"""Gets all the world objects, finds the enemies, then
	figures out which one is closest to the player's current
	position. Dumb calculation, does not take map into account.
	"""
	
	playerData = getAction('player')
	worldObjectData = getAction('world/objects')
	
	enemies = []
	
	for worldObject in worldObjectData:
		if worldObject['typeId'] >= 3000:
			enemies.append(worldObject)

	logging.debug('Found {} enemies'.format(len(enemies)))
	
	nearestEnemy = None
	nearestEnemyDistance = 999999.0
	
	for enemy in enemies:
		distance = distanceBetweenPoints(
			playerData["position"]["x"],
			playerData["position"]["y"],
			enemy["position"]["x"],
			enemy["position"]["y"]
		)
		
		if distance < nearestEnemyDistance:
			logging.debug('Found a new nearest enemy - {}, {} @ {} x {}'.format(
				enemy['id'],
				enemy['type'],
				enemy["position"]["x"],
				enemy["position"]["y"]				
			))
			nearestEnemy = enemy
			nearestEnemyDistance = distance
	
	return nearestEnemy


def reorientPlayer(angle, attempts=10, pause=1, accuracy=10):
	"""Try and make the player point in a specific direction
	"""
	
	for i in range(attempts):
		currentData = getAction('player')
		
		diff = currentData["angle"] - angle
		
		"""If we would spin >180 degrees, go the other way"""
		if diff > 180:
			diff -= 360
		
		logging.debug('We are facing {} and want to be facing {}, difference of {}'.format(currentData["angle"], angle, diff))
		
		if abs(diff) < accuracy:
			logging.debug('Close enough - angle is {} vs {}'.format(currentData["angle"], angle))
			return True
		
		"""Game units are roughly 105 in a circle"""
		spinAmount = int(float(diff) * float(105.0 / 360.0))
			
		spinPlayer(spinAmount)
		
		time.sleep(pause)

	logging.debug('Gave up - angle is {} vs {}'.format(currentData["angle"], angle))
	
	return False

	

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

enemy = findNearestEnemy()
reorientPlayer(0)
moveToPoint(enemy["position"]["x"], enemy["position"]["y"])
shoot()
