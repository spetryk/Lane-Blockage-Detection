
from network_setup_hardcode import *
import numpy as np
import os
import csv
import time


vehLength = 15.0 	# Average length of vehicle, in feet
detectorInfoFile = 'NetworkInfoFiles/detectorInfoFile.csv'
detectorDataFilePath = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/'
detectorDataFile = detectorDataFilePath + 'DetectorData_2017-06-23 140518.csv'

def main():
	
	global detectorInfoFile
	global detectorDataFile

	# Outline Aimsun network: connections between intersections, approaches, movements, and detectors
	intersectionDict, detectorDict = initializeNetwork(detectorInfoFile)

	# At each time step:
	
	# Add flow and occupancy data to correct detectors
	# Get line from csv detector file

	watch = True		# Set watch to True if you want to look for new files
	newFile = None
	if watch:
		newFile = get_new_file(detectorDataFilePath)
	print(newFile)

	read_data_realtime(newFile)

	for intrsct in intersectionDict.values():
		for app in intrsct.approaches.values():
			for mvmt in app.movements.values():

				# Estimate traffic state for each movement
				# Check advanced detectors
				#adv_state = estimateMovementState(mvmt, timeStep=0, category='Advanced')
			
				pass

def get_new_file(directory):
	# Watch directory for new detector data file (appears when simulation starts)
	# Returns path to file that just appeared
	
	before = dict([(file, None) for file in os.listdir(directory)])	 # Find files already in directory

	while True:
		time.sleep(10)
		# Find differences in directory before and after time step
		after = dict([(file, None) for file in os.listdir(directory)])

		new = {newFile : after[newFile] for newFile in set(after)-set(before)}	
		if len(new) > 1:
			raise Exception('More than one new data file appeared')				# Only handle one new file per time step

		if bool(new):
			# New file appeared (dictionary is not empty)
			data = next(iter(new.keys()))	# Name of new data file 
			return directory + data

		before = after



def read_data_realtime(detectorDataFile):
	# Read lines from Aimsun simulation detector data as they appear
	# detectorDataFile: .csv file (make sure to include correct directory)

	with open(detectorDataFile, 'r') as dataFile:
		fileReader = csv.reader(dataFile, delimiter=',')
		dataFile.seek(0,2) 		# Go to end of file
		i = 0
		while i<5:
			row = dataFile.readline()	# Check if there's a new line to read
			if not row:
				time.sleep(0.1) 	# Stop looking briefly
				print(i)
				i = i + 1

				continue
			print(row)
			i = i + 1

		#next(dataFile)	# Skip header row


def calculate_critical_occupancies(detector, turn):
	# Set critical occupancies for detector: two thresholds for advanced, one threshold for stopbar
	# Does not return value; instead, modifies detector.criticalOccs field in place

	# detector: Detector object
	# turn: 'Left', 'Through', or 'Right'

	global vehLength

	# Set variables needed in equation
	L = vehLength			# feet
	D = detector.length 	# feet
	G = detector.movements[turn].greenTime 								# seconds
	C = detector.movements[turn].approach.intersection.cycleTime    	# seconds
	h = detector.movements[turn].headway								# seconds
	v_sat_sb = detector.movements[turn].satVelocityStopbar 				# miles per hour
	v_sat_adv = detector.movements[turn].satVelocityAdvanced 			# miles per hour

	if detector.category == 'Advanced':
		# Two critical occupancies
		occ_crit_1 = ((L+D)*3600 / (v_sat_adv*5280))  * (1.0/h) * (G/C)
		occ_crit_2 = ((L+D)*3600 / (v_sat_adv*5280))  * (1.0/h) * (G/C) + ((C-G)/C)
		detector.criticalOccs = [occ_crit_1, occ_crit_2]

	else:
		# Stopbar detector, only one critical occupancy
		occ_crit = ((L+D) / (v_sat_sb*5280*3600))  * (1.0/h) + ((C-G)/C)
		detector.criticalOccs.append(occ_crit)

	# criticalOccs field of given detector object now contains array of critical occupancies


def estimateMovementState(mvmt, timeStep, category):
	# Estimate traffic state of movement's detectors at given time for specified category
		# mvmt: Movement object
		# time: desired time (int)
		# category: 'Advanced' or 'Stopbar'

	# Returns string: 'Uncongested' or 'Congested'

	direction = mvmt.direction	# 'Left', 'Through', or 'Right'
	occs = np.array([])
	occ_crits = np.array([])
	for det in mvmt.detectors.values():	
		# Average the occupancies from all advanced detectors with information for this movement
		if det.category == category:
			print(det.occupancy[timeStep])
			occs = np.append(occs, det.occupancy[time])				# Actual occupancies at this time step
			calculate_critical_occupancies(det, mvmt.direction)		
			first_occ_crit = det.criticalOccs[0]					# First critical occupancy (separates uncongested & congested)
			occ_crits = np.append(occ_crits, first_occ_crit)

	avg_occ = np.mean(occs)
	avg_occ_crit = np.mean(occ_crits)

	if np.isnan(avg_occ):
		raise Exception('No ' + category + 'detectors for this movement')
	
	if avg_occ < avg_occ_crit:
		return 'Uncongested'
	else:
		return 'Congested'


if __name__ == '__main__':
	main()