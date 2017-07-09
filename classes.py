# Classes needed for lane blockage detection


# To do notes:
# 	- check if arguments for fields are null
#	- only set fields if they are given, otherwise None
#	- designate fields as public/private


class Intersection():

	def __init__(self, externalID, cycleTime, approaches=None):

		self.externalID = externalID
		self.cycleTime = cycleTime
		self.approaches = approaches


class Approach():

	def __init__(self, intersection=None, movements=None):

		self.intersection = intersection  # Intersection this approach is part of
		self.movements = movements        # Movements part of approach


class Movement():

	def __init__(self, direction, satVelocity, detectors=None, approach=None):

		self.direction = direction 		# 'Left', 'Through', or 'Right'
		self.satVelocity = satVelocity  # saturation velocity, in mph
		self.detectors = detectors		# Detectors with data for this movement
		self.approach = approach        # Approach this movement is part of (Approach object)


class Detector():

	def __init__(self, externalID, category, length, movements=None):

		self.externalID = externalID
		self.category = category			# 'Advanced' or 'Stopbar'
		self.length = length				# Length, in feet
		self.movements = movements  		# Movements detector covers	(array of Movement objects)

		self.flow = []
		self.occupancy = []

