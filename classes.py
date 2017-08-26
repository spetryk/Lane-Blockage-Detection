# Classes needed for lane blockage detection


# To do notes:
# 	- check if arguments for fields are null
#	- designate fields as public/private
#   - account for permitted left turns


class Intersection():

	def __init__(self, externalID, cycleTime, approaches=None):

		self.externalID = externalID	# External ID of intersection (e.g. 2000)
		self.cycleTime = cycleTime		# Cycle time of control plan, in seconds

		if approaches==None:
			self.approaches = {}
		else:
			self.approaches = approaches	# Approaches part of this intersection (dictionary)

class Approach():

	def __init__(self, sectionID, intersection=None, movements=None):

		self.sectionID = sectionID 		  # ID of section
		self.intersection = intersection  # Intersection this approach is part of (Intersection object)

		if movements==None:
			self.movements={}
		else:
			self.movements = movements    # Movements part of approach (dictionary: {direction : Movement})

class Movement():

	def __init__(self, direction, greenTime, satVelocityStopbar, satVelocityAdvanced, headway, numUpLanes, numDownLanes, detectors=None, approach=None):

		self.direction = direction 						# 'Left', 'Through', or 'Right'
		self.greenTime = greenTime						# Green time for this movement, in seconds (assume left turns are all protected)
		self.headway = headway							# Headway, in seconds
		self.satVelocityStopbar = satVelocityStopbar	# Saturation velociy for stopbar movement, in miles per hour
		self.satVelocityAdvanced = satVelocityAdvanced	# Saturation velocity for advanced movement, in miles per hour
		self.numUpLanes = numUpLanes					# Number of upstream lanes for this movement (to be covered by advanced detectors)
		self.numDownLanes = numDownLanes 				# Number of downstream lanes for this movement (to be covered by stopbar detectors)
		self.approach = approach        				# Approach this movement is part of (Approach object)

		if detectors==None:
			self.detectors={}
		else:
			self.detectors = detectors		# Detectors with data for this movement (dictionary: {externalID : Detector})

class Detector():

	def __init__(self, externalID, category, length, movements=None):

		self.externalID = externalID		# Detector external ID (e.g. 100005)
		self.category = category			# 'Advanced' or 'Stopbar'
		self.length = length				# Length, in feet

		if movements==None:
			self.movements={}
		else:
			self.movements = movements  	# Movements detector covers	(dictionary)

		self.flow = []						# Flow, in vehicles per hour
		self.occupancy = []					# Occupancy (percent)
		self.time = []

		# Calculated critical occupancies for each turn covered by detector (one critical occ for stopbar, two for advanced)
		self.criticalOccs = {'Left':None, 'Through':None, 'Right':None}		
		
		self.currentState = None			# Current traffic state ('Uncongested' or 'Queue Spillback' for stopbar,
											# 'Uncongested', 'Congested', or 'Queue Spillback' for advanced)
