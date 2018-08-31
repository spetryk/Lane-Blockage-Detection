import pandas as pd 

df = pd.DataFrame(columns=('Time', 'SectionID', 'Conclusion'))
#print(df)

LB_Conclusions2 = {'Time':[], 'SectionID':[], 'Conclusion':[]}

LB_Conclusions2['Time'].append(800)
LB_Conclusions2['SectionID'].append(818)
LB_Conclusions2['Conclusion'].append('No Information')

df2 = pd.DataFrame(LB_Conclusions2)
df = df.append(df2)
#print(df)

LB_Conclusions2['Time'].append(1600)
LB_Conclusions2['SectionID'].append(828)
LB_Conclusions2['Conclusion'].append('No Lane Blockage')

df2 = pd.DataFrame(LB_Conclusions2)


a = ['Left', 'Through']
#print(' '.join(a))

message = ''
for turn in a:
	message = message + turn + ' '

b = 'Lane Blockage by Queue Spillback from ' + '{} {}'.format(*a)

set_a = set([])
#print(set_a)
#print(len(set_a))
set_a.update(set([1,2]))
#print(set_a)
b = [2,3,4]
set_a.update(b)
#print(set_a)

#print(len(set_a.intersection([7,8])))

spillback_turns = {'Right', 'Left'}
#print(' '.join(spillback_turns))

a = [1,2,5]
#print(max(a))

detectorDataFilePath = 'C:/Users/suzep/Dropbox/Aimsun_calibration/Model/sim_output/'

#print(detectorDataFilePath + 'DetectorData_2017-07-10 132656_some_sb.csv')

sb_states = {'Left': ['Uncongested'], 'Through': ['Uncongested', 'Uncongested']}
#sb_states = {'Right': 'Uncongested', 'Left': 'Uncongested', 'Through': 'Uncongested'}
#print(sum(turn=='Uncongested' for turn in sb_states.values()))

#print(sum(value=='Uncongested' for turn in sb_states.values() for value in turn))
#print(all(value=='Uncongested' for turn in sb_states.values() for value in turn))

sb_states =  {'Left': ['Uncongested'], 'Through': ['Uncongested', 'Queue Spillback']}
print(any(state=='Queue Spillback' for state in sb_states['Through']))


keys = list(sb_states.keys())
movements = ['Left','Through','Right']
print(set(movements) - set(keys))

# if False:
# 	print('here')
# #a = 5
# elif a==5:
# 	print('a is 5')
# else:
# 	print('else')
