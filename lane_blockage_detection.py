
from network_setup_hardcode import *


vehLength = 15.0 	# Average length of vehicle, in feet
detectorInfoFile = 'NetworkInfoFiles/detectorInfoFile2.csv'

def main():
	
	global detectorInfoFile

	# Outline Aimsun network: connections between intersections, approaches, movements, and detectors
	intersectionDict, detectorDict = initializeNetwork(detectorInfoFile)

	calculate_critical_occupancies(detectorDict[100002], 'Left')
	print(detectorDict[100002].criticalOccs)

	


def calculate_critical_occupancies(detector, turn):
	# detector: Detector object
	# turn: 'Left', 'Through', or 'Right'

	global vehLength

	# Set variables needed in equation
	L = vehLength			# feet
	D = detector.length 	# feet
	G = detector.movements[turn].greenTime 							# seconds
	C = detector.movements[turn].approach.intersection.cycleTime    # seconds
	h = detector.movements[turn].headway							# seconds
	v_sat = detector.movements[turn].satVelocity 					# miles per hour

	if detector.category == 'Advanced':
		occ_crit = ((L+D) / (v_sat*5280*3600))  * (1.0/h) * (G/C)
		detector.criticalOccs.append(occ_crit)

	occ_crit = ((L+D) / (v_sat*5280*3600))  * (1.0/h) + ((C-G)/C)
	detector.criticalOccs.append(occ_crit)



if __name__ == '__main__':
	main()