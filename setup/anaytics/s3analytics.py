import boto3
import json
import subprocess
import itertools
import operator
from itertools import groupby 
import os

Days = range(1,32)
# print Days
days_dict= dict.fromkeys(Days)

def most_common(lst):
    return max(set(lst), key=lst.count)

#automate command line argument
#aws s3 ls --summarize --human-readable --recursive s3://bucket-name/directory
#sort by most recent
#aws s3api list-objects --bucket mybucketfoo --query "reverse(sort_by(Contents,&LastModified))"

humandata = os.popen('aws s3 ls --summarize --human-readable --recursive s3://raspcam-archive/human > human.txt').read()
weapondata = os.popen('aws s3 ls --summarize --human-readable --recursive s3://raspcam-archive/weapons > weapons.txt').read()
fpdata = os.popen('aws s3 ls --summarize --human-readable --recursive s3://raspcam-archive/false_positive > false_positive.txt').read()

#HUMAN ARRAYS 
hyear = []
hmonth = []
hday = []
hhour = []

#WEAPONS ARRAYS
wyear = []
wmonth = []
wday = []
whour = []

#FALSE_POSITIVE ARRAYS
fpyear = []
fpmonth = []
fpday = []
fphour = []

#store output of commnands as textfiles 
human_file = open('human.txt','r+')
weapon_file = open('weapons.txt','r+')
fp_file = open('false_positive.txt','r+')


for line in human_file:
	newarr = line.split()
	if newarr == []:
		break
	#print (ymd)
	#hms = newarr[1]
	#year is [0, 0-3] #month is [0, 5-6] #day is [0, 8-9] #hour is [1, 0-1] #minute is [1, 3-4] #seconds is [1, 6-7]
	hyear.append(newarr[0][0:4])
	hmonth.append(newarr[0][5:7])
	hday.append(newarr[0][8:10])
	hhour.append(newarr[1][0:2])


for line in weapon_file:
	newarr2 = line.split()
	if newarr2 == []:
		break
	#print (ymd)
	#hms = newarr[1]
	#year is [0, 0-3] #month is [0, 5-6] #day is [0, 8-9] #hour is [1, 0-1] #minute is [1, 3-4] #seconds is [1, 6-7]
	wyear.append(newarr2[0][0:4])
	wmonth.append(newarr2[0][5:7])
	wday.append(newarr2[0][8:10])
	whour.append(newarr2[1][0:2])


for line in fp_file:
	newarr3 = line.split()
	if newarr3 == []:
		break
	#print (ymd)
	#hms = newarr[1]
	#year is [0, 0-3] #month is [0, 5-6] #day is [0, 8-9] #hour is [1, 0-1] #minute is [1, 3-4] #seconds is [1, 6-7]
	fpyear.append(newarr3[0][0:4])
	fpmonth.append(newarr3[0][5:7])
	fpday.append(newarr3[0][8:10])
	fphour.append(newarr3[1][0:2])

# print (hyear)
# print (hmonth)
# print (hday)
# print (hhour)
# print "Most common year:", (most_common(hyear))
# print "Most common month:", (most_common(hmonth))
# print "Most common day:", (most_common(hday))
# print "Most common hour:", (most_common(hhour))


#percent weapons among false positives
humanobjects = os.popen('aws s3 ls s3://raspcam-archive/human/ --recursive --summarize | grep -o "Total Objects.*" | cut -f2- -d:').read()
fpobjects = os.popen('aws s3 ls s3://raspcam-archive/false_positive/ --recursive --summarize | grep -o "Total Objects.*" | cut -f2- -d:').read()
weaponobjects = os.popen('aws s3 ls s3://raspcam-archive/weapons/ --recursive --summarize | grep -o "Total Objects.*" | cut -f2- -d:').read()
# print "Total humans detected: ", humanobjects
# print "Total false positives: ",fpobjects
# print "Total weapons detected: ", weaponobjects


def getValue():
	del hday[0]
	for day in days_dict:
		days_dict[day] = 0
	for day in hday:
		day = int(day)
		days_dict[day]+=1
	return days_dict
	# print days_dict


getValue()

                           
