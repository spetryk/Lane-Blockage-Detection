
from network_setup_hardcode import *


vehLength = 15.0 	# Average length of vehicle

def main():
	
	initializeNetwork()		# Outline Aimsun network: connections between intersections, approaches, movements, and detectors



def estimateState(detector, turn):
	# detector: Detector object
	# turn: 'Left', 'Through', or 'Right'

	global vehLength

	# Calculate critical occupancy
	L = vehLength
	D = detector.length
	G = detector.movements[turn].greenTime
	C = detector.movements[turn].approach.intersection.cycleTime
	h = 5


if __name__ == '__main__':
	main()