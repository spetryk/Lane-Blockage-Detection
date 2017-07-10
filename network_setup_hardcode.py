from classes import *
import csv

# Initialize setup for Aimsun testing network
# Create relationships between Intersections, Approaches, Movements, and Detectors

def initializeNetwork(detectorInfoFile):
	# ********** Initialize network setup *****************

	# Intersections
	intersectionDict = {1000: Intersection(externalID = 1000, cycleTime = 90.0), 2000 : Intersection(externalID = 2000, cycleTime = 90.0)}

	# Approaches
	intersectionDict[1000].approaches[828] = Approach(sectionID=828, intersection=intersectionDict[1000])
	intersectionDict[1000].approaches[825] = Approach(sectionID=825, intersection=intersectionDict[1000])

	intersectionDict[2000].approaches = {} # Bug: 1000's approaches were being applied to 2000's as well, so clear 2000 before assigning
	intersectionDict[2000].approaches[826] = Approach(sectionID=826, intersection=intersectionDict[2000])
	intersectionDict[2000].approaches[818] = Approach(sectionID=818, intersection=intersectionDict[2000])


	# Movements
	intersectionDict[1000].approaches[828].movements = {'Left': Movement(direction='Left',greenTime=20.0,satVelocityStopbar=20.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[1000].approaches[828]),
													'Through': Movement(direction='Through',greenTime=50.0,satVelocityStopbar=25.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[1000].approaches[828]),
													 'Right': Movement(direction='Right',greenTime=20.0,satVelocityStopbar=20.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[1000].approaches[828])}
	intersectionDict[1000].approaches[825].movements = {'Left': Movement(direction='Left',greenTime=20.0,satVelocityStopbar=20.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[1000].approaches[825]),
													'Through': Movement(direction='Through',greenTime=50.0,satVelocityStopbar=25.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[1000].approaches[825]),
													 'Right': Movement(direction='Right',greenTime=20.0,satVelocityStopbar=20.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[1000].approaches[825])}
	intersectionDict[2000].approaches[826].movements = {'Left': Movement(direction='Left',greenTime=20.0,satVelocityStopbar=20.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[2000].approaches[826]),
													'Through': Movement(direction='Through',greenTime=50.0,satVelocityStopbar=25.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[2000].approaches[826]),
													 'Right': Movement(direction='Right',greenTime=20.0,satVelocityStopbar=20.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[2000].approaches[826])}
	intersectionDict[2000].approaches[818].movements = {'Left': Movement(direction='Left',greenTime=20.0,satVelocityStopbar=20.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[2000].approaches[818]),
													'Through': Movement(direction='Through',greenTime=50.0,satVelocityStopbar=25.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[2000].approaches[818]),
													 'Right': Movement(direction='Right',greenTime=20.0,satVelocityStopbar=20.0,satVelocityAdvanced=30,headway=2.3,approach=intersectionDict[2000].approaches[818])}

	# Detectors

	# Store detectors in dictionary: key = external ID, value = Detector object
	detectorDict = {}

	with open(detectorInfoFile, 'rt') as detFile:
		fileReader = csv.reader(detFile, delimiter = ',')
		next(detFile) # Skip header row
		for row in fileReader:
			intrsct = int(row[0])			# Intersection detector is in
			sectID = int(row[1])		# Section detector is in
			extID = int(row[2])			# Detector external ID
			category = row[3]			# Advanced or stopbar
			length = float(row[4])		# Length, in ft

			detectorDict[extID] = Detector(externalID=extID, category=category, length=length)

			movements = row[5].split(',')	# Any combination of: [Left, Through, Right]
			for turn in movements:
				# Add Detector object to correct place in network
				intersectionDict[intrsct].approaches[sectID].movements[turn].detectors[extID] = detectorDict[extID]

				# Set movement field of Detector to be able to traverse up network
				detectorDict[extID].movements[turn] = intersectionDict[intrsct].approaches[sectID].movements[turn]

	return intersectionDict, detectorDict