
from network_setup_hardcode import *
import numpy as np
import pandas as pd
import os
import csv
import time

vehLength = 15.5 	# Average length of vehicle, in feet
detectorInfoFile = 'NetworkInfoFiles/detectorInfoFile.csv'
detectorDataFilePath = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/'
#data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656.csv'
#data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656_some_adv.csv' # Removed detectors 1, 2, 17, 18
data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656_some_sb.csv'	# Removed  detectors 13, 14, 15, 16
#data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656_no_adv.csv'	# Removed all advanced detectors

# Outline Aimsun network: connections between intersections, approaches, movements, and detectors
intersectionDict, detectorDict = initializeNetwork(detectorInfoFile)

# Initialize empty dictionary for conclusions
LB_Conclusions = {'Time':[], 'SectionID':[], 'Conclusion':[]}


def main():
	
	global detectorInfoFile
	global data
	global LB_Conclusions
	global intersectionDict
	global detectorDict


	# At each time step:
	
	# Add flow and occupancy data to correct detectors
	# Get line from csv detector file

	watch = False		# Set watch to True if you want to look for new files
	newFile = None
	if watch:
		newFile = get_new_file(detectorDataFilePath)
	
	if bool(newFile):
		# Monitor current simulation's data
		read_data_realtime(newFile) # <--In here: option to search in real time

# ********** Get lane blockage detection working for completed simulation first (not real time) ********************
	times = read_completed_file(data, detectorDict)

	# Determine lane blockage conclusion at each time step for each approach, add to LB_Conclusions dictionary

	for timeStep in times:		# For each time, calculate current states
		for intrsct in intersectionDict.values():
			#print(intrsct.approaches.values())
			for app in intrsct.approaches.values():
				#print(app.sectionID)
				make_LB_conclusion(timeStep, intrsct, app)

		#print('time: ',timeStep)
		#print(LB_Conclusions)

	LB_DataFrame = pd.DataFrame(LB_Conclusions)
	LB_table = LB_DataFrame.pivot(index='Time',columns='SectionID',values='Conclusion')
	print(LB_table)


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
	# Returns first critical occupancy only (second one not needed in algorithm)

	# detector: Detector object
	# turn: 'Left', 'Through', or 'Right'

	global vehLength

	# Set variables needed in equation
	L = float(vehLength)			# feet
	D = float(detector.length) 	# feet
	G = float(detector.movements[turn].greenTime) 								# seconds
	C = float(detector.movements[turn].approach.intersection.cycleTime)    	# seconds
	h = float(detector.movements[turn].headway)								# seconds
	v_sat_sb = float(detector.movements[turn].satVelocityStopbar) 				# miles per hour
	v_sat_adv = float(detector.movements[turn].satVelocityAdvanced) 			# miles per hour

	if detector.category == 'Advanced':
		# Two critical occupancies, but only need the first one
		occ_crit = ((L+D)*3600.0 / (v_sat_adv*5280.0))  * (1.0/h) * (G/C)
		#occ_crit_2 = ((L+D)*3600 / (v_sat_adv*5280))  * (1.0/h) * (G/C) + ((C-G)/C)

	else:
		# Stopbar detector, only one critical occupancy
		occ_crit = ((L+D)*3600.0 / (v_sat_sb*5280.0))  * (1.0/h) + ((C-G)/C)

	return occ_crit

def estimate_movement_state(mvmt, curr_time, debug, category):
	# Estimate traffic state of movement's detectors at given time for specified category
		# mvmt: Movement object
		# curr_time: current time (int)
		# category: 'Advanced' or 'Stopbar'

	# Returns array of states (e.g. ['Uncongested', 'Congested']), or None if there was insufficient data

	global intersectionDict
	global detectorDict

	direction = mvmt.direction	# 'Left', 'Through', or 'Right'
	states = []

	for det in mvmt.detectors.values():	
		# Determine state for all detectors in this category with information for this movement
		if det.category == category:
			print('det.category: ',det.category) if debug else None # **********************************************************
			try:
				index = np.where(det.time == curr_time)[0][0]		# Find index in detector's occupancy array that corresponds to the current time
			except IndexError:
				# No data at this time step for this detector
				print('IndexError, time: ',curr_time,' det.time: ',det.time) if debug else None # **********************************************************
				#print('Missing data for ' + category + ' ' + mvmt.direction + ' turn of section ' + str(mvmt.approach.sectionID))
				return None

			curr_occ = det.occupancy[index]							# Current occupancy
			first_occ_crit = calculate_critical_occupancies(det, mvmt.direction)	

			#first_occ_crit = det.criticalOccs[0]					# First critical occupancy (separates uncongested & spillback for stopbar, 
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
		#print('Not enough ' + category + ' detectors for ' + mvmt.direction + ' turn of section ' + str(mvmt.approach.sectionID))
		#bprint('Not enough lanes, numLanes: ',dict_adv_states) if debug else None # **********************************************************
		return None
	else:
		return states


def make_LB_conclusion(timeStep, intrsct, app):

	global LB_Conclusions
	global intersectionDict
	global detectorDict

	debug = app.sectionID==828

	# Initialize dictionaries for advanced and stopbar states: {turn: states}
	dict_adv_states = {'Left':None, 'Through':None, 'Right':None}
	dict_sb_states = {'Left':None, 'Through':None, 'Right':None}

	# Check advanced detectors: if any do not have information, conclude 'No Information'
	for mvmt in app.movements.values():
		print('Movement: ',mvmt) if debug else None # **********************************************************
		adv_states = estimate_movement_state(mvmt, timeStep, debug, category='Advanced')
		print('adv_states: ', adv_states) if debug else None # ******************************************************
		if adv_states == None:
			# Approach does not have full advanced detector coverage
			LB_Conclusions['Conclusion'].append('No Information')
			LB_Conclusions['Time'].append(timeStep)
			LB_Conclusions['SectionID'].append(app.sectionID)
			return

		dict_adv_states[mvmt.direction] = adv_states
		print('dict_adv_states: ',dict_adv_states) if debug else None # **********************************************************

	# Now have determined states for all available advanced detectors
	all_states = [state for each_mvmt in dict_adv_states.values() for state in each_mvmt]	# Flattens states into one list
	if all(state=='Uncongested' for state in all_states):
		# All advanced detectors are uncongested
		LB_Conclusions['Conclusion'].append('No Lane Blockage')
		LB_Conclusions['Time'].append(timeStep)
		LB_Conclusions['SectionID'].append(app.sectionID)
		return
	else:
		# Check stopbar detectors
		for mvmt in app.movements.values():
			print('turn of mvmt: ',mvmt.direction) if debug else None # **********************************************************
			sb_states = estimate_movement_state(mvmt, timeStep, debug, category='Stopbar')
			dict_sb_states[mvmt.direction] = sb_states

	# Now have determined states for all available stopbar detectors
	print('dict_sb_states: ',dict_sb_states) if debug else None # **********************************************************

	# Check if all stopbar detectors had no data
	if all(state==None for state in dict_sb_states.values()):
		# No data for stopbar detectors; insufficient information	
		LB_Conclusions['Conclusion'].append('Lane Blockage by Unknown Downstream Traffic')
		LB_Conclusions['Time'].append(timeStep)
		LB_Conclusions['SectionID'].append(app.sectionID)
		return

	# Check if any stopbar detectors had queue spillback
	spillback_movements = []

	for turn in dict_sb_states.keys():
		if dict_sb_states[turn] is not None and any(state=='Queue Spillback' for state in dict_sb_states[turn]):
			# Movement had queue spillback
			spillback_movements.append(turn)
	if spillback_movements != []:
		# Conclude Lane Blockage by Movement(s) with Queue Spillback
		LB_Conclusions['Conclusion'].append('Lane Blockage by Queue Spillback from ' + ' '.join(spillback_movements) + ' Movements')
		LB_Conclusions['Time'].append(timeStep)
		LB_Conclusions['SectionID'].append(app.sectionID)
			

if __name__ == '__main__':
	main()