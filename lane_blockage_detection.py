
from network_setup_hardcode import *
import numpy as np
import pandas as pd
import os
import csv
import time

vehLength = 17.0 	# Average length of vehicle, in feet
detectorInfoFile = 'NetworkInfoFiles/detectorInfoFile.csv'
detectorDataFilePath = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/'
data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656.csv'
#data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656_some_adv.csv' # Removed detectors 1, 2, 17, 18
#data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656_half_sb_at_one_app.csv'	# Removed  detectors 15, 16
#data = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/DetectorData_2017-07-10 132656_some_sb.csv'	# Removed  detectors 13, 14, 15, 16
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


# ********** Get lane blockage detection working for completed simulation first (not real time) ********************
	times = read_detector_file(data, detectorDict)

	# Determine lane blockage conclusion at each time step for each approach, add to LB_Conclusions dictionary

	for timeStep in times:		
		for intrsct in intersectionDict.values():
			for app in intrsct.approaches.values():
				make_LB_conclusion(timeStep, intrsct, app)

	LB_DataFrame = pd.DataFrame(LB_Conclusions)
	LB_table = LB_DataFrame.pivot(index='Time',columns='SectionID',values='Conclusion')
	LB_table.to_csv('LB Conclusions.csv')
	print(LB_table)

def make_LB_conclusion(timeStep, intrsct, app):

	global LB_Conclusions
	global intersectionDict
	global detectorDict


	# Initialize dictionaries for advanced and stopbar states: {turn: states}
	dict_adv_states = {'Left':None, 'Through':None, 'Right':None}
	dict_sb_states = {'Left':None, 'Through':None, 'Right':None}

	# Check advanced detectors: if any do not have information, conclude 'No Information'
	for mvmt in app.movements.values():
		adv_states = estimate_movement_state(mvmt, timeStep, category='Advanced')

		if adv_states == None:
			# Approach does not have full advanced detector coverage
			LB_Conclusions['Conclusion'].append('No Information')
			LB_Conclusions['Time'].append(timeStep)
			LB_Conclusions['SectionID'].append(app.sectionID)
			return

		dict_adv_states[mvmt.direction] = adv_states

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
			sb_states = estimate_movement_state(mvmt, timeStep, category='Stopbar')
			dict_sb_states[mvmt.direction] = sb_states

	# Now have determined states for all available stopbar detectors

	# Check if all stopbar detectors had no data
	if all(state==None for state in dict_sb_states.values()):
		# No data for stopbar detectors
		concl_type = determine_type(app, timeStep)
		LB_Conclusions['Conclusion'].append(concl_type + ' by Unknown Downstream Traffic')
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
		return

	# Check how many movements have data
	numMoves = sum(bool(turn) for turn in dict_sb_states.values())

	if numMoves == 1:
		concl_type = determine_type(app, timeStep)
		LB_Conclusions['Conclusion'].append(concl_type + ' by Unknown Downstream Traffic')
		LB_Conclusions['Time'].append(timeStep)
		LB_Conclusions['SectionID'].append(app.sectionID)
		return
	elif numMoves == 2:
		# Check if both moves are uncongested
		if sum(turn=='Uncongested' for turn in dict_sb_states.values()) == 2:
			concl_type = determine_type(app, timeStep)
			LB_Conclusions['Conclusion'].append(concl_type + ' by Unknown Downstream Traffic')
			LB_Conclusions['Time'].append(timeStep)
			LB_Conclusions['SectionID'].append(app.sectionID)
			return
		else:
			concl_type = determine_type(app, timeStep)
			LB_Conclusions['Conclusion'].append(concl_type + ' by movement with missing data OR between stopbar and advanced detectors')
			LB_Conclusions['Time'].append(timeStep)
			LB_Conclusions['SectionID'].append(app.sectionID)
			return
	else:
		# All 3 movements have data
		# Check if all uncongested
		if sum(turn=='Uncongested' for turn in dict_sb_states.values()) == 3:
			concl_type = determine_type(app, timeStep)
			LB_Conclusions['Conclusion'].append(concl_type + ' between stopbar and advanced detectors')
			LB_Conclusions['Time'].append(timeStep)
			LB_Conclusions['SectionID'].append(app.sectionID)
			return
		else:
			# Find which movement has lowest distance to stopbar
			distance_dict = {}
			for mvmt in app.movements.values():
				curr_dist = dist_to_sb(mvmt, timeStep)
				distance_dict[mvmt.direction] = curr_dist

			most_congested_mvmt = min(distance_dict, key=distance_dict.get)
			concl_type = determine_type(app, timeStep)
			LB_Conclusions['Conclusion'].append(concl_type + ' by ' + most_congested_mvmt + ' Movement')
			LB_Conclusions['Time'].append(timeStep)
			LB_Conclusions['SectionID'].append(app.sectionID)
			return



def estimate_movement_state(mvmt, curr_time, category):
	# Estimate traffic state of movement's detectors at given time
	# Returns None if a detector is dead or movement doesn't have full detector coverage

	global detectorDict

	direction = mvmt.direction	# 'Left', 'Through', or 'Right'
	states = []

	for det in mvmt.detectors.values():	
		if det.category == category:
			# Determine state for all detectors in this category with information for this movement
			det_state = estimate_detector_state(det, curr_time, mvmt.direction, category)
			if det_state==None:
				return None
			states.append(det_state)

	# Check how many lanes the detectors need to cover for this movement
	numLanes = mvmt.numUpLanes if category=='Advanced' else mvmt.numDownLanes

	if len(states) < numLanes:
		# Not enough detectors in this category for full coverage of this movement
		# print('Not enough ' + category + ' detectors for ' + mvmt.direction + ' turn of section ' + str(mvmt.approach.sectionID))
		return None
	else:
		return states


def calculate_critical_occupancies(detector, turn):
	# Calculate critical occupancies for detector
	# turn: 'Left', 'Through', or 'Right'

	global vehLength

	# Set variables needed in equation
	L = float(vehLength)			# feet
	D = float(detector.length) 		# feet
	G = float(detector.movements[turn].greenTime) 							# seconds
	C = float(detector.movements[turn].approach.intersection.cycleTime)    	# seconds
	h = float(detector.movements[turn].headway)								# seconds
	v_sat_sb = float(detector.movements[turn].satVelocityStopbar) 			# miles per hour
	v_sat_adv = float(detector.movements[turn].satVelocityAdvanced) 		# miles per hour

	if detector.category == 'Stopbar':
		occ_crit = ((L+D)*3600.0 / (v_sat_sb*5280.0))  * (1.0/h) * (G/C) + ((C-G)/C)
		occupancies = [occ_crit*100, None]
		detector.criticalOccs = occupancies

		return occupancies

	# If here: category=='Advanced'
	occ_crit_1 = ((L+D)*3600.0 / (v_sat_sb*5280.0))  * (1.0/h) * (G/C)
	occ_crit_2 = ((L+D)*3600.0 / (v_sat_sb*5280.0))  * (1.0/h) * (G/C) + ((C-G)/C)

	occupancies = [occ_crit_1*100, occ_crit_2*100]
	detector.criticalOccs = occupancies

	return occupancies


def determine_type(app, curr_time):
	# 'Lane Blockage' if any advanced detectors have queue spillback
	# '___ % Congested' otherwise

	for mvmt in app.movements.values():
		mvmt_states = estimate_movement_state(mvmt, curr_time, 'Advanced')
		# If any advanced detectors have queue spillback, type = Lane Blockage
		if 'Queue Spillback' in mvmt_states:
			return 'Lane Blockage'

	# Otherwise: advanced detector(s) congested, so calculate average % congestion
	percent_congestion = []
	for mvmt in app.movements.values():
		for det in mvmt.detectors.values():
			if det.category == 'Advanced':
				det_state = estimate_detector_state(det, curr_time, mvmt.direction, 'Advanced')
				if (det_state is not None) and (det_state=='Congested'):
					# If detector is congested, calculate % congestion		
					index = np.where(det.time == curr_time)[0][0]		# Find index in detector's occupancy array that corresponds to the current time
					curr_occ = det.occupancy[index]						# Current occupancy
					curr_percent_congestion = [(abs(curr_occ - (det.criticalOccs[1]-det.criticalOccs[0])) / (det.criticalOccs[1]-det.criticalOccs[0]))*100]
					percent_congestion = percent_congestion + [curr_percent_congestion]

	avg_percent_congestion = round(np.mean(percent_congestion), 2) # Get average, round to 2 decimal places

	return str(avg_percent_congestion) + ' % Congested'

def estimate_detector_state(det, curr_time, turn, category):
	# Determine traffic state for this detector
	try:
		index = np.where(det.time == curr_time)[0][0]		# Find index in detector's occupancy array that corresponds to the current time
	except IndexError:
		# No data at this time step for this detector
		#print('Missing data for ' + category + ' ' + mvmt.direction + ' turn of section ' + str(mvmt.approach.sectionID))
		return None

	curr_occ = det.occupancy[index]							# Current occupancy
	critical_occs = calculate_critical_occupancies(det, turn)

	if curr_occ < critical_occs[0]:
		return 'Uncongested'

	elif category=='Advanced' and curr_occ < critical_occs[1]:
		return 'Congested'
	else:
		return 'Queue Spillback'

def dist_to_sb(mvmt, curr_time):
	# Returns average distance of stopbar detectors

	distances = []

	for det in mvmt.detectors.values():
		if det.category == 'Stopbar':
			det_state = estimate_detector_state(det, curr_time, mvmt.direction, 'Stopbar')
			if (det_state is not None) and (det_state=='Uncongested'):
				# If detector is uncongested, calculate distance to stopbar critical occupancy		
				index = np.where(det.time == curr_time)[0][0]		# Find index in detector's occupancy array that corresponds to the current time
				curr_occ = det.occupancy[index]						# Current occupancy
				curr_dist = [(det.criticalOccs[0] - curr_occ) / det.criticalOccs[0]]
				distances = distances + [curr_dist]

	avg_dist = round(np.mean(distances), 2) # Get average, round to 2 decimal places

	return avg_dist

def read_detector_file(detectorDataFile, detectorDict):
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


if __name__ == '__main__':
	main()