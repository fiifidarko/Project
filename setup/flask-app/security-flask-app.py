import boto3, json
from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template
import json
import subprocess
import itertools
import operator
from itertools import groupby 
import os


with open('/home/fiifi/Desktop/4813/PROJECT/IoTCamera/setup/aws_config/config.json') as aws_config:
	data = json.load(aws_config)

AWS_KEY= data.get('AWS_KEY', '')
AWS_SECRET= data.get('AWS_SECRET', '')
REGION = data.get('REGION', '')
BUCKET = data.get('BUCKET', '')

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

# returns the number of images taken during each day of the current month
def getDaysValues():
	# create a dictionary in which {key = day of month : value = number images taken during day of month}
	Days = range(1,32)
	days_dict = dict.fromkeys(Days)
	
	# the first data value is always invalid
	del hday[0]
	
	# initialize all values to 0 (to avoid value == None)
	for day in days_dict:
		days_dict[day] = 0
		
	# count the number of images taken during each day of the month
	for day in hday:
		day = int(day)
		days_dict[day] += 1
	
	return days_dict

# returns the number of images taken during each month of the current year
def getMonthsValues():
	# create a dictionary in which {key = month of year : value = number images taken during month of year}
	Months = range(1,13)
	months_dict = dict.fromkeys(Months)
	
	# the first data value is always invalid
	del hmonth[0]
	
	# initialize all values (to avoid value == None)
	for month in months_dict:
		months_dict[month] = 0
	
	# count the number of images taken during each day of the month
	for month in hmonth:
		month = int(month)
		months_dict[month] += 1
		
	return months_dict
	

#################### FLASK APP ####################
app = Flask(__name__)
 
@app.route("/")
def chart():
    # various labels to be used with the graphs rendering data
    # labels_months = {"January": 1,"February": 2,"March": 3,"April": 4,"May": 5,"June": 6,"July": 7,"August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    labels_months = ["January","February","March","April","May","June","July","August", "September", "October", "November", "December"]    
    labels_categories = ["People Spotted","False Alarm"]
    #range_of_months = range(1,13)
    range_of_days = range(1,32)

    # populate data_days[] with the number of images taken during each day of month [index = day of month, value = number images taken during day of month]
    values = getDaysValues()
    data_days = range(1,32)
    for count in range(1,32):
    	data_days[count] = values[count]
	
    # populate data_months[] with the number of images taken during each month [index = month, value = number images taken during month]
    values = getMonthsValues()
    data_months = range(1,13) 
    for count in range(1,13):
    	data_months[count] = values[count]

    # populate data_categories[] with the number of human images and false positive images
    data_categories = [humanobjects, fpobjects]

    # we are removing the fourth graph
    labels4 = {"January": 1,"February": 2,"March": 3,"April": 4,"May": 5,"June": 6,"July": 7,"August": 8, "September": 9, "October": 10, "November": 11, "December": 12}    
    values4 = [10,9,8,7,6,4,7,8]
	
    # the last two arguments representing the fourth graph should be removed
    return render_template('chart.html', values=data_days, labels=range_of_days, values2=data_months, labels2=labels_months,
    	values3=data_categories, labels3=labels_categories, values4=values4, labels4=labels4)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
