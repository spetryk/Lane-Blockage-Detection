from classes import *
import csv
import os

# ********** Initialize network setup *****************

# Intersections
intersectionDict = {'West': Intersection(externalID = 1000, cycleTime = 90), 'East' : Intersection(externalID = 2000, cycleTime = 90)}



# Approaches
approachDict = {}
approachInfoFile = 'NetworkInfoFiles/approachInfoFile.csv'

with open(approachInfoFile, 'rt') as appFile:
	fileReader = csv.reader(appFile, delimiter = ',')
	next(appFile)	# Skip header row
	for row in fileReader:
		sectID = int(row[0])
		intersection = row[1]
		# Create entry in approach dictionary corresponding to the section
		approachDict[sectID] = Approach(sectionID = sectID, intersection = intersectionDict[intersection], movements={})
		intersectionDict[intersection].approaches.append(approachDict[sectID])

		for i in range(2,len(row)):
			if row[i] != '':
				mvmtInfo = row[i].split(',')
				direction = mvmtInfo[0]
				mvmt = Movement(direction=direction, greenTime=mvmtInfo[1], satVelocity=mvmtInfo[2])
				approachDict[sectID].movements[direction] = mvmt
print(intersectionDict['East'].approaches)

# Detectors
detectorInfoFile = 'NetworkInfoFiles/detectorInfoFile.csv'

# Store detectors in dictionary: key = external ID, value = Detector object
detectorDict = {}

with open(detectorInfoFile, 'rt') as detFile:
	fileReader = csv.reader(detFile, delimiter = ',')
	next(detFile) # Skip header row
	for row in fileReader:
		intrsct = row[0]
		sectID = row[1]
		extID = row[2]
		category = row[3]	# Advanced or stopbar
		length = row[4]		# Length, in ft
		for i in range(5,len(row)):
			if row[i] != '':
				#intersectionDict[intrsct].
				mvmtInfo = row[i].split(',')
				mvmt = Movement(direction=mvmtInfo[0], greenTime=mvmtInfo[1], satVelocity=mvmtInfo[2])
				

		#detectorDict[extID] = Detector(externalID=extID, category=category, length=length, movements=movements)


# Movements

