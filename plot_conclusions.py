# Classify decision scheme conclusions into broader categories (lane blockage, heavy/moderate/light congestion, uncongested, no information)

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import pylab as pl


class Conclusion():
	def __init__(self,curr_time, movements=None, congestionLevel=None, congestionNumber=None, marker=None, QSB=None):
		self.curr_time = curr_time
		self.movements = {} if movements == None else movements
		self.congestionLevel = congestionLevel
		self.congestionNumber = congestionNumber 
			# 0: No Information
			# 1: Uncongested
			# 2: Light Congestion
			# 3: Moderate Congestion
			# 4: Heavy Congestion
			# 5: Lane Blockage
		self.marker = marker
			# Marker on scatterplot: 
				# 'L' for left movement, 'T' for Through, 'R' for right, 'o' otherwise
				# Can be any combination of L,T,R: e.g. 'TR' for Through and Right movements
		self.QSB = QSB

def main():
	fileName = 'Case1.csv'
	data = pd.read_csv('Conclusions/' + fileName, header=0, names=['Time','Conclusion'])
	allConclusions = []

	movementKeywords = ['Unknown', 'Left', 'Through', 'Right']

	for index,row in data.iterrows():
		concl_string = row.Conclusion
		congLevel, congNumber = determine_congestion(row.Conclusion)
		movements = [word for word in concl_string.split() if word in movementKeywords]
		if movements==[]:
			# No information, or uncongested: use simple 'o' as marker
			marker = 'o'
		else:
			# Marker is first letter of each movement
			letters = [word[0] for word in movements]
			marker = '$' + ''.join(letters) + '$'
		qsb = 'Yes' if 'Queue Spillback' in concl_string else None
		concl = Conclusion(curr_time=row.Time, movements=movements, congestionLevel=congLevel, 
			congestionNumber=congNumber, marker=marker, QSB=qsb)
		allConclusions.append(concl)

	make_plots(allConclusions)

def determine_congestion(conclusion):
	if conclusion == 'No Information':
		congLevel = 'No Information'
		congNumber = 0
	elif conclusion == 'No Lane Blockage or Congestion':
		congLevel = 'Uncongested'
		congNumber = 1
	elif 'Lane Blockage' in conclusion:
		congLevel = 'Lane Blockage'
		congNumber = 5
	else:
		# Determine if Light, Moderate, or Heavy congestion
		percentage = float(conclusion.split('%')[0])
		if percentage < 33.33:
			congLevel = 'Light'
			congNumber = 2
		elif percentage < 66.66:
			congLevel = 'Moderate'
			congNumber = 3
		else:
			congLevel = 'Heavy'
			congNumber = 4
	return congLevel, congNumber

def make_plots(allConclusions):

	matplotlib.rcParams.update({'font.size': 18})
	categories = ('No Information', 'Uncongested', 'Light', 'Moderate', 'Heavy', 'Lane Blockage')
	y = [0, 1, 2, 3, 4, 5]

	fig1 = pl.figure(1)	# 12 AM - 6 AM
	x = [0, 7200, 14400, 21600]
	plt.xticks(x, ('12 AM', '2 AM', '4 AM', '6 AM'))
	plt.yticks(y, categories)
	pl.ylim([0, 5.5])

	fig2 = pl.figure(2) # 6 AM - 12 PM
	x = [21600, 28800, 36000, 43200]
	plt.xticks(x, ('6 AM', '8 AM', '10 AM', '12 PM'))
	plt.yticks(y, categories)
	pl.ylim([0, 5.5])
	
	fig3 = pl.figure(3)	# 12 PM - 6 PM
	x = [43200, 50400, 57600, 64800]
	plt.xticks(x, ('12 PM', '2 PM', '4 PM', '6 PM'))
	plt.yticks(y, categories)
	pl.ylim([0, 5.5])


	for concl in allConclusions:
		# Plot only first time category for now
		if concl.curr_time < 22200:
			pl.figure(1)
		elif concl.curr_time < 43800:
			pl.figure(2)
		else:
			pl.figure(3)

		color = 'r' if concl.QSB != None else 'k'
		plt.scatter(concl.curr_time, concl.congestionNumber, s=90, marker=concl.marker, edgecolors=color, facecolors='k')
	
	plt.show()


if __name__=='__main__':
	main()

