
from network_setup_hardcode import *
import numpy as np
import os
import csv
import time
from collections import namedtuple

vehLength = 15.5 	# Average length of vehicle, in feet
detectorInfoFile = 'NetworkInfoFiles/detectorInfoFile.csv'
detectorDataFilePath = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/'
#data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656.csv'
data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656_no_adv.csv'

def main():
	
	global detectorInfoFile

	# Outline Aimsun network: connections between intersections, approaches, movements, and detectors
	intersectionDict, detectorDict = initializeNetwork(detectorInfoFile)


	# At each time step:
	
	# Add flow and occupancy data to correct detectors
	# Get line from csv detector file

	watch = False		# Set watch to True if you want to look for new files
	newFile = None
	if watch:
		newFile = get_new_file(detectorDataFilePath)
	
	if bool(newFile):
		# Monitor current simulation's data
		read_data_realtime(newFile)


# ********** Get lane blockage detection working for completed simulation first (not real time) *********************
	global data

	times = read_completed_file(data, detectorDict)

	# Store lane blockage conclusions in dictionary
		# Keys: tuple of (time, sectionID) -> allows you to find lane blockage conclusion at certain time for a certain approach
		# Values: conclusion (string: e.g. 'No Lane Blockage')
	LB_Key = namedtuple("LB_Key", ("curr_time", "section_ID"))

	# Initialize empty dictionary for conclusions
	LB_Conclusions = {}	

	# Determine lane blockage conclusion at each time step for each approach, add to LB_Conclusions dictionary

	for timeStep in times:		# For each time, calculate current states
		for intrsct in intersectionDict.values():
			for app in intrsct.approaches.values():

				make_LB_Conclusion(timeStep, intrsct, app)

	# approach828 = [concl for concl in LB_Conclusions if concl.desired_section_ID==828]
	# print(approach828)
	


def read_completed_file(detectorDataFile, detectorDict):
	# Read in data from completed simulation before calling algorithm
	# Format: DetectorAimsunID, DetectorFieldID, Time(sec), Flow(vph), Occupancy, in %

	times = np.array([])		# Return array of unique time steps

	with open(detectorDataFile, 'r') as dataFile:
		fileReader = csv.reader(dataFile, delimiter=',')
		next(dataFile)		# Skip header row

		for row in fileReader:
			extID = int(row[1])
			curr_time = int(row[2])
			curr_flow = float(row[3])
			curr_occ = float(row[4])

			det = detectorDict[extID]		# Detector object for this row
			det.time.append(curr_time)
			det.flow.append(curr_flow)
			det.occupancy.append(curr_occ)
	
			times = np.append(times, curr_time)

	return np.unique(times)

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
	# Read detector data from Aimsun simulation as they appear
	# detectorDataFile: .csv file (full path)

	with open(detectorDataFile, 'r') as dataFile:
		fileReader = csv.reader(dataFile, delimiter=',')
		dataFile.seek(0,2) 		# Go to end of file
		
		while True:
			row = dataFile.readline()	# Check if there's a new line to read
			if not row:
				time.sleep(0.1) 	# Stop looking briefly
				continue
			print(row)
			

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


def estimate_movement_state(mvmt, curr_time, category):
	# Estimate traffic state of movement's detectors at given time for specified category
		# mvmt: Movement object
		# curr_time: current time (int)
		# category: 'Advanced' or 'Stopbar'

	# Returns string: 'Uncongested' or 'Queue Spillback' for Stopbar, 
	#				  'Uncongested' or 'Congested' for Advanced

	direction = mvmt.direction	# 'Left', 'Through', or 'Right'
	states = []

	for det in mvmt.detectors.values():	
		# Determien state for all detectors in this category with information for this movement
		if det.category == category:
			index = np.where(det.time == curr_time)[0][0]			# Find index in detector's occupancy array that corresponds to the current time
			curr_occ = det.occupancy[index]							# Current occupancy
			calculate_critical_occupancies(det, mvmt.direction)	
			first_occ_crit = det.criticalOccs[0]					# First critical occupancy (separates uncongested & spillback for stopbar, 
																	#   						uncongested & congested for advanced)
			if curr_occ < first_occ_crit:
				states.append('Uncongested')
			elif category == 'Advanced':
				# Advanced detector, avg_occ >= avg_occ_crit
				states.append('Congested')
			else:
				# Stopbar detector, avg_occ >= avg_occ_crit
				states.append('Queue Spillback')

		# Check how many lanes the detectors need to cover for this movement
		numLanes = mvmt.numUpLanes if category=='Advanced' else mvmt.numDownLanes

		if len(states) < numLanes:
			# Not enough detectors in this category for full coverage of this movement
			print('Not enough ' + category + ' detectors for ' + mvmt.direction + ' turn of section ' + str(mvmt.approach.sectionID))
			return None
		else:
			return states

	# # Take averages of occupancies
	# avg_occ = np.mean(occs)
	# avg_occ_crit = np.mean(occ_crits)

	# if avg_occ < avg_occ_crit:
	# 	return 'Uncongested'
	# elif category == 'Advanced':
	# 	# Advanced detectorm avg_occ >= avg_occ_crit
	# 	return 'Congested'
	# else:
	# 	# Stopbar detector, avg_occ >= avg_occ_crit
	# 	return 'Queue Spillback'

def make_LB_conclusion(timeStep, intrsct, app):
	# Get key for lane blockage conclusions dictionary (LB_Conclusions)
	key = LB_Key(timeStep, app.sectionID)

	# Initialize dictionary for stopbar states: {turn: stopbar states}
	turn_sb_states = {'Left':None, 'Through':None, 'Right':None}

	for mvmt in app.movements.values():
		# Check advanced detectors: if any do not have information, conclude 'No Information'
		adv_states = estimate_movement_state(mvmt, timeStep, category='Advanced')
		
		if adv_states == None:
			# Approach does not have full advanced detector coverage
			LB_Conclusions[key] = 'No Information'
			return
		elif all(state=='Uncongested' for state in adv_state):
			# All advanced detectors are uncongested
			LB_Conclusions[key] = 'No Lane Blockage' 
			return
		else:
			# Check stopbar detectors
			sb_states = estimate_movement_state(mvmt, timeStep, category='Stopbar')
			turn_sb_states[mvmt.direction] = sb_states

	# Now have determined states for all available stopbar detectors
	if sb_states == None:
		# No data for stopbar detectors; insufficient information
		LB_Conclusions[key] = 'Lane Blockage by Unknown Downstream Traffic'	
		return
			



if __name__ == '__main__':
	main()