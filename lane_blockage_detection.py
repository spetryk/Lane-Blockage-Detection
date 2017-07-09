from classes import *
import csv

# ********** Initialize network setup *****************
# Initialize network from bottom up: Detectors -> Movements -> Approaches -> Intersections


# Detectors
detectorInfoFile = 'detectorInfoFile.csv'
detectorDict = {}

with open(detectorInfoFile, 'rt') as detFile:
	fileReader = csv.reader(detFile)
	for row in fileReader:
		extID = row([0])
		category = row([1])
		length = row([2])

		detectorDict[extID] = Detector(externalID=extID, category=category, length=length)


print(detectorDict)

# Intersections
West = Intersection(externalID = 1000, cycleTime = 90)
