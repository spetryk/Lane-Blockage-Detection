# Classes needed for lane blockage detection


# To do notes:
# 	- check if arguments for fields are null
#	- designate fields as public/private
#   - account for permitted left turns


class Intersection():

	def __init__(self, externalID, cycleTime, approaches={}):

		self.externalID = externalID	# External ID of intersection (e.g. 2000)
		self.cycleTime = cycleTime		# Cycle time of control plan, in seconds
		self.approaches = approaches	# Approaches part of this intersection (dictionary)


class Approach():

	def __init__(self, sectionID, intersection=None, movements={}):

		self.sectionID = sectionID 		  # ID of section
		self.movements = movements        # Movements part of approach (dictionary: {direction : Movement})
		self.intersection = intersection  # Intersection this approach is part of (Intersection object)

class Movement():

	def __init__(self, direction, greenTime, satVelocityStopbar, satVelocityAdvanced, headway, detectors={}, approach=None):

		self.direction = direction 		# 'Left', 'Through', or 'Right'
		self.greenTime = greenTime		# Green time for this movement, in seconds (assume left turns are all protected)
		self.headway = headway			# Headway, in seconds
		self.satVelocityStopbar = satVelocityStopbar	# Saturation velociy for stopbar movement, in miles per hour
		self.satVelocityAdvanced = satVelocityAdvanced	# Saturation velocity for advanced movement, in miles per hour
		self.detectors = detectors		# Detectors with data for this movement (dictionary: {externalID : Detector})
		self.approach = approach        # Approach this movement is part of (Approach object)


class Detector():

	def __init__(self, externalID, category, length, movements={}):

		self.externalID = externalID		# Detector external ID (e.g. 100005)
		self.category = category			# 'Advanced' or 'Stopbar'
		self.length = length				# Length, in feet
		self.movements = movements  		# Movements detector covers	(dictionary)

		self.flow = []
		self.occupancy = []

		self.criticalOccs = []				# Calculated critical occupancies (one for stopbar, two for advanced)

