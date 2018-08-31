# Classify decision scheme conclusions into broader categories (lane blockage, heavy/moderate/light congestion, uncongested, no information)

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


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
				# 'L' for left movement, 'T' for Through, 'R' for right, '.' otherwise
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
			# No information, or uncongested: use simple '.' as marker
			marker = '.'
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

	# fig = plt.figure()
	# ax = fig.add_subplot(111)    # The big subplot
	# ax1 = fig.add_subplot(211)
	# ax2 = fig.add_subplot(212)
	# ax3 = fig.add_subplot(213)

	fig, axes = plt.subplots(3,1,sharey='col')
	dummy = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
	red_rec = Rectangle((0, 0), 1, 1, fc="r")
	leg = fig.legend(handles=[dummy,dummy,dummy,dummy,red_rec],
	 labels=['$U$    Unknown Downstream Traffic       ', '$L$    Left Movement',
	  '$T$    Through Movement', '$R$    Right Movement','Queue Spillback'],
	  loc='upper center', fontsize=16, ncol=3, bbox_to_anchor=(0.5,1)) 

	plt.setp(axes, yticks=[0, 1, 2, 3, 4, 5], 
		yticklabels=['   No Information', '   Uncongested', '   Light', '   Moderate', '   Heavy', '   Lane Blockage'])

	plt.sca(axes[0])
	x = [0, 3600, 7200, 10800, 14400, 18000, 21600]
	plt.xticks(x, ('12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM'))
	minorLocator = MultipleLocator(1800)
	axes[0].xaxis.set_minor_locator(minorLocator)
	plt.ylim([0,5.5])
	plt.grid(which='major', linestyle='--')
	plt.grid(which='minor',axis='x')

	plt.sca(axes[1])
	x = [21600, 25200, 28800, 32400, 36000, 39600, 43200]
	plt.xticks(x, ('6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM'))
	plt.ylim([0,5.5])
	minorLocator = MultipleLocator(1800)
	axes[1].xaxis.set_minor_locator(minorLocator)
	axes[1].set_ylabel('Congestion Level')
	plt.grid(which='major', linestyle='--')
	plt.grid(which='minor',axis='x')

	plt.sca(axes[2])
	x = [43200, 46800, 50400, 54000, 57600, 61200, 64800]
	plt.xticks(x, ('12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM'))
	plt.ylim([0,5.5])
	minorLocator = MultipleLocator(1800)
	axes[2].xaxis.set_minor_locator(minorLocator)
	axes[2].set_xlabel('Time')
	plt.grid(which='major', linestyle='--')
	plt.grid(which='minor',axis='x')


	for concl in allConclusions:
		color = 'r' if concl.QSB != None else 'k'
		if concl.curr_time < 22200:
			plt.sca(axes[0])
		elif concl.curr_time < 43800:
			plt.sca(axes[1])
		else:
			plt.sca(axes[2])

		plt.scatter(concl.curr_time, concl.congestionNumber, s=150*(len(concl.marker.replace('$',''))), marker=concl.marker, edgecolors=color, facecolors='k')
	
	plt.show()


if __name__=='__main__':
	main()

