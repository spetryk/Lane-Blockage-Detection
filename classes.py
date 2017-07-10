# Classes needed for lane blockage detection


# To do notes:
# 	- check if arguments for fields are null
#	- only set fields if they are given, otherwise None
#	- designate fields as public/private
#   - account for permitted left turns


class Intersection():

	def __init__(self, externalID, cycleTime, approaches={}):

		self.externalID = externalID	# External ID of intersection
		self.cycleTime = cycleTime		# Cycle time of control plan, in seconds
		self.approaches = approaches	# Approaches part of this intersection (dictionary)


class Approach():

	def __init__(self, sectionID, intersection=None, movements={}):

		self.sectionID = sectionID 		  # ID of section
		self.intersection = intersection  # Intersection this approach is part of
		self.movements = movements        # Movements part of approach (dictionary)


class Movement():

	def __init__(self, direction, greenTime, satVelocity, headway, detectors={}, approach=None):

		self.direction = direction 		# 'Left', 'Through', or 'Right'
		self.greenTime = greenTime		# Green time for this movement (assume left turns are all protected)
		self.satVelocity = satVelocity  # saturation velocity, in mph
		self.headway = headway
		self.detectors = detectors		# Detectors with data for this movement (dictionary)
		self.approach = approach        # Approach this movement is part of (Approach object)


class Detector():

	def __init__(self, externalID, category, length, movements={}):

		self.externalID = externalID
		self.category = category			# 'Advanced' or 'Stopbar'
		self.length = length				# Length, in feet
		self.movements = movements  		# Movements detector covers	(dictionary)

		self.flow = []
		self.occupancy = []

