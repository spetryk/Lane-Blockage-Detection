
from network_setup_hardcode import *


vehLength = 15.0 	# Average length of vehicle, in feet
detectorInfoFile = 'NetworkInfoFiles/detectorInfoFile.csv'

def main():
	
	global detectorInfoFile

	# Outline Aimsun network: connections between intersections, approaches, movements, and detectors
	intersectionDict, detectorDict = initializeNetwork(detectorInfoFile)


	# At each time step: 
		# Estimate traffic state for each movement
			# Check advanced detectors
			# 
			# Average data from each detector in that movement

	# print(detectorDict[200019].category)
	# calculate_critical_occupancies(detectorDict[200019], 'Left')
	# print(detectorDict[200019].criticalOccs)

	


def calculate_critical_occupancies(detector, turn):
	# Set critical occupancies for detector: two thresholds for advanced, one threshold for stopbar

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

def estimateMovementState(mvmt):
	# Estimate traffic state of movement
		# 

	direction = mvmt.direction	# 'Left', 'Through', or 'Right'

	for det in mvmt.detectors:
		# Average the occupancies from 


if __name__ == '__main__':
	main()