import pandas as pd 

df = pd.DataFrame(columns=('Time', 'SectionID', 'Conclusion'))
print(df)

LB_Conclusions2 = {'Time':[], 'SectionID':[], 'Conclusion':[]}

LB_Conclusions2['Time'].append(800)
LB_Conclusions2['SectionID'].append(818)
LB_Conclusions2['Conclusion'].append('No Information')

df2 = pd.DataFrame(LB_Conclusions2)
df = df.append(df2)
print(df)

LB_Conclusions2['Time'].append(1600)
LB_Conclusions2['SectionID'].append(828)
LB_Conclusions2['Conclusion'].append('No Lane Blockage')

df2 = pd.DataFrame(LB_Conclusions2)


a = ['Left', 'Through']
print(' '.join(a))

message = ''
for turn in a:
	message = message + turn + ' '

b = 'Lane Blockage by Queue Spillback from ' + '{} {}'.format(*a)

