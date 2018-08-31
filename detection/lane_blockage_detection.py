
from network_setup_hardcode import *
import numpy as np
import pandas as pd
import os
import csv
import time

VEH_LENGTH = 17.0 	# Average length of vehicle, in feet
CLEARANCE = 9.10	# Average distance between stopped vehicles, in feet
detectorInfoFile = 'NetworkInfoFiles/detectorInfoFile.csv'
detectorDataFilePath = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/'

# Data from LB Test #1 (LT and RT blockages on Section 826)
#data = detectorDataFilePath + 'DetectorData_2017-07-10 132656.csv'
#data = detectorDataFilePath + 'DetectorData_2017-07-10 132656_some_adv.csv' # Removed detectors 1, 2, 17, 18
#data = detectorDataFilePath + 'DetectorData_2017-07-10 132656_one_mvmt_missing.csv'	# Removed  detector 16
#data = detectorDataFilePath + 'DetectorData_2017-07-10 132656_half_sb_at_one_app.csv'	# Removed  detectors 15, 16
#data = detectorDataFilePath + 'DetectorData_2017-07-10 132656_some_sb.csv'	# Removed  detectors 13, 14, 15, 16
#data = detectorDataFilePath + 'DetectorData_2017-07-10 132656_no_adv.csv'	# Removed all advanced detectors

# Data from LB Test #4 (LT blockage on Section 826)
#data = detectorDataFilePath + 'DetectorData_2017-07-13 160215.csv'
#data = detectorDataFilePath + 'DetectorData_2017-07-14 115950.csv'	# Trial run: constant demand
#data = detectorDataFilePath + 'DetectorData_2017-07-14 124533.csv'	# Det. 16 is 22 ft
#data = detectorDataFilePath + 'DetectorData_2017-07-14 132502.csv'	# Clearance is 7.10 ft instead of 9.10


# Data from LB Test #6 (Testing approach on Section 826)
#data = detectorDataFilePath + 'DetectorData_2017-07-17 100658.csv' # Trial 2
#data = detectorDataFilePath + 'DetectorData_2017-07-17 103952.csv'	# Trial 3
#data = detectorDataFilePath + 'DetectorData_2017-07-17 115545.csv'	# Trial 4: some queue spillback for TH on 826

#data = detectorDataFilePath + 'DetectorData_2017-07-17 133619.csv'	# Trial 5, Case 3: full stopbar detector coverage
#data = detectorDataFilePath + 'DetectorData_2017-07-17 133619_only_LT.csv' # Trial 5: no detectorss 13, 14, 15 (only LT on section 826)
#data = detectorDataFilePath + 'DetectorData_2017-07-17 133619_Case4.csv' # Trial 5, Case 4: no detector 13 (right turn stopbar on section 826)


# Data from LB Test #7 (Testing approach on Section 825)
#data = detectorDataFilePath + 'DetectorData_2017-07-31 112301.csv'			# Trial 1, Case 1
data = detectorDataFilePath + 'DetectorData_2017-07-31 112301_Case2.csv'	# Trial 1, Case 2 (Removed detectors 9, 10)


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


# ***************** Lane blockage detection scheme for completed simulation (not real time) ********************
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


	# Check advanced detectors: if any do not have information, conclude 'No Information'
	for mvmt in app.movements.values():
		adv_states = estimate_movement_state(mvmt, timeStep, category='Advanced')

		if adv_states == None:
			# Approach does not have full advanced detector coverage
			LB_Conclusions['Conclusion'].append('No Information')
			LB_Conclusions['Time'].append(timeStep)
			LB_Conclusions['SectionID'].append(app.sectionID)
			return

	# Now have determined states for all available advanced detectors 

	# Check if all advanced detectors are uncongested, using the MAX green time out of this approach's movements to find critical occupancies
	if uncongested_approach_check(app, timeStep):
		# All advanced detectors are uncongested based off MAX green time
		LB_Conclusions['Conclusion'].append('No Lane Blockage or Congestion')
		LB_Conclusions['Time'].append(timeStep)
		LB_Conclusions['SectionID'].append(app.sectionID)
		return
	else:
		# Check stopbar detectors
		# Initialize dictionary for stopbar states: {turn: states}
		dict_sb_states = {}

		for mvmt in app.movements.values():
			sb_states = estimate_movement_state(mvmt, timeStep, category='Stopbar')
			if sb_states is not None:
				dict_sb_states[mvmt.direction] = sb_states

	# Now have determined states for all available stopbar detectors

	# Check how many movements have data
	numMoves = len(dict_sb_states.keys())

	# Check if all stopbar detectors had no data
	if numMoves == 0:
		concl_type = determine_type(app, timeStep)
		LB_Conclusions['Conclusion'].append(concl_type + ' by Unknown Downstream Traffic')
		LB_Conclusions['Time'].append(timeStep)
		LB_Conclusions['SectionID'].append(app.sectionID)
		return

	# Check if any stopbar detectors had queue spillback
	spillback_movements = []
	for turn in dict_sb_states.keys():
		if any(state=='Queue Spillback' for state in dict_sb_states[turn]):
			spillback_movements.append(turn)

	if spillback_movements != []:
		# Case: Movement(s) with Queue Spillback
		spillback_turns = set()
		for turn in spillback_movements:
			spillback_turns.update(find_lane_group(app, turn))

		concl_type = determine_type(app, timeStep)
		LB_Conclusions['Conclusion'].append(concl_type + ' with Queue Spillback from ' + ' '.join(spillback_turns) + ' Movements')
		LB_Conclusions['Time'].append(timeStep)
		LB_Conclusions['SectionID'].append(app.sectionID)
		return

	if numMoves < 3:
		# Not full detector coverage at stopbar
		concl_type = determine_type(app, timeStep)
		LB_Conclusions['Conclusion'].append(concl_type + ' by Unknown Downstream Traffic')
		LB_Conclusions['Time'].append(timeStep)
		LB_Conclusions['SectionID'].append(app.sectionID)
		return

	else:
		# Full detector coverage at stopbar
		# Find which movement has occupancy closest to stopbar critical occupancy
		distance_dict = {}
		for mvmt in app.movements.values():
			curr_dist = distance_to_stopbar(mvmt, timeStep)
			distance_dict[mvmt.direction] = curr_dist

		most_congested_mvmt = min(distance_dict, key=distance_dict.get)
		lane_group = find_lane_group(app, most_congested_mvmt)

		concl_type = determine_type(app, timeStep)
		LB_Conclusions['Conclusion'].append(concl_type + ' by ' + ' '.join(lane_group) + ' Movement(s)')
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


def estimate_detector_state(det, curr_time, turn, category, maxGreen=None):
	# Determine traffic state for this detector
	try:
		# Find index in detector's occupancy array that corresponds to the current time
		index = np.where(det.time == curr_time)[0][0]
	except IndexError:
		# No data at this time step for this detector
		#print('Missing data for ' + category + ' ' + mvmt.direction + ' turn of section ' + str(mvmt.approach.sectionID))
		return None

	curr_occ = det.occupancy[index]	  # Current occupancy
	crit_occs = calculate_critical_occupancies(det, turn, maxGreen)

	if curr_occ < crit_occs[0]:
		det.currentState = 'Uncongested'
		return 'Uncongested'

	elif category=='Advanced' and curr_occ < crit_occs[1]:
		det.currentState='Congested'
		return 'Congested'
	else:
		det.currentState='Queue Spillback'
		return 'Queue Spillback'


def uncongested_approach_check(app, curr_time):
	# Returns True if all advanced detectors are uncongested using the MAX green time over all movements, False otherwise

	# Find max green time
	mvmts = list(app.movements.values())
	maxGreen = max([mvmt.greenTime for mvmt in mvmts])

	# Find advanced detectors for this approach
	adv_dets = set([]) 
	for mvmt in app.movements.values():
		for detector in mvmt.detectors.values():
			if detector.category=='Advanced':
				adv_dets.update([detector])

	# adv_set contains set of advanced detectors for this approach
	adv_set = set(adv_dets)
	adv_states = []
	for detector in adv_set:
		for turn in detector.movements.keys():
			adv_states.append(estimate_detector_state(detector, curr_time, turn, category='Advanced', maxGreen=maxGreen))

	return(all(state=='Uncongested' for state in adv_states))


def calculate_critical_occupancies(detector, turn, maxGreen=None):
	# Set detector's criticalOccs field to calculated occupancies for each individual turn
	# turn: 'Left', 'Through', or 'Right'
	# maxGreen: maximum green time for any movement at this approach
		# (only provide maxGreen argument when checking if advanced detectors are uncongested)
	
	global VEH_LENGTH
	global CLEARANCE

	# Set variables needed in equation
	
	L = float(VEH_LENGTH)							# feet
	D = float(detector.length)				 		# feet
	G = maxGreen if maxGreen is not None else float(detector.movements[turn].greenTime)	# seconds
	C = float(detector.movements[turn].approach.intersection.cycleTime)    				# seconds
	h = float(detector.movements[turn].headway)											# seconds
	v_sat_sb = float(detector.movements[turn].satVelocityStopbar) 						# miles per hour
	v_sat_adv = float(detector.movements[turn].satVelocityAdvanced) 					# miles per hour

	# If detector length is too long, raise critical occupancy to account for errors
	error_correction = 1				# No errors accounted for
	if D > (L+CLEARANCE):
		error_correction = 1.05 		# Account for 5 % error if the detector is too long to distinguish vehicles

	if detector.category == 'Stopbar':
		if maxGreen is not None:
			raise Exception('Cannot use max green time to calculate critical occs for stopbar detectors!')

		occ_crit = ((L+D)*3600.0 / (v_sat_sb*5280.0))  * (1.0/h) * (G/C) + ((C-G)/C)
		occupancies = [min(occ_crit*100*error_correction,100), None]	# Max critical occupancy is 100 %
		detector.criticalOccs[turn] = occupancies
		return occupancies

	# If here: category=='Advanced'
	occ_crit_1 = ((L+D)*3600.0 / (v_sat_adv*5280.0))  * (1.0/h) * (G/C)
	occ_crit_2 = ((L+D)*3600.0 / (v_sat_adv*5280.0))  * (1.0/h) * (G/C) + ((C-G)/C)

	occupancies = [occ_crit_1*100*error_correction, min(occ_crit_2*100*error_correction,100)]

	if maxGreen is None:
		detector.criticalOccs[turn] = occupancies

	return occupancies


def determine_type(app, curr_time):
	# 'Lane Blockage' if any advanced detectors have queue spillback
	# '___ % Congested' otherwise

	for mvmt in app.movements.values():
		mvmt_states = estimate_movement_state(mvmt, curr_time, 'Advanced')
		# If any advanced detectors have queue spillback, type = Lane Blockage
		if 'Queue Spillback' in mvmt_states:
			return 'Lane Blockage'

	# Otherwise: advanced detector(s) congested; find most congested detector and return its % congestion
	percent_congestion = []
	for mvmt in app.movements.values():
		for det in mvmt.detectors.values():
			if det.category == 'Advanced':
				det_state = estimate_detector_state(det, curr_time, mvmt.direction, 'Advanced')
				if (det_state is not None) and (det_state=='Congested'):
					# If detector is congested, calculate % congestion		
					index = np.where(det.time == curr_time)[0][0]		# Find index in detector's occupancy array that corresponds to the current time
					curr_occ = det.occupancy[index]						# Current occupancy
					crit_occs = det.criticalOccs[mvmt.direction]
					curr_percent_congestion = [((curr_occ - crit_occs[0]) / (crit_occs[1]-crit_occs[0])) * 100]
					percent_congestion = percent_congestion + [curr_percent_congestion]

	max_percent_congestion = round(max(percent_congestion)[0],2)	# Get % congestion from most congested detector, round to 2 decimal places
	#avg_percent_congestion = round(np.mean(percent_congestion), 2) # Get average, round to 2 decimal places

	return str(max_percent_congestion) + ' % Congested'


def distance_to_stopbar(mvmt, curr_time):
	# Returns distance of occupancy to stopbar critical occupancy, averaged over all detectors covering this movement

	distances = []

	for det in mvmt.detectors.values():
		if det.category == 'Stopbar':
			if (det.currentState is not None) and (det.currentState=='Uncongested'):
				# If detector is uncongested, calculate distance to stopbar critical occupancy		
				index = np.where(det.time == curr_time)[0][0]		# Find index in detector's occupancy array that corresponds to the current time
				curr_occ = det.occupancy[index]						# Current occupancy
				curr_dist = [(det.criticalOccs[mvmt.direction][0] - curr_occ) / det.criticalOccs[mvmt.direction][0]]
				distances = distances + [curr_dist]

	avg_dist = round(np.mean(distances), 5) # Get average, round to 5 decimal places

	return avg_dist


def find_lane_group(app, turn):
	# Find all movements that share the detectors of the given turn

	dets_in_turn = set([]) # set of detector external IDS of given turn
	turn_set = set([turn]) # set of turns which have chosen detectors

	for mvmt in app.movements.values():
		sb_dets = []
		for detector in mvmt.detectors.values():
			if detector.category=='Stopbar':
				# This is a stopbar detector
				sb_dets.append(detector.externalID)
				if mvmt.direction == turn:
					# This is a stopbar detector in the specific turn
					dets_in_turn.update([detector.externalID])

		sb_set = set(sb_dets)
		if len(dets_in_turn.intersection(sb_dets)) > 0:
			# Detector(s) in common
			turn_set.update([mvmt.direction])

	return turn_set
	

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