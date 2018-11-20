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

                           




# FLASK APP 
app = Flask(__name__)
 
@app.route("/")
def chart():
    
    labels = {"January": 1,"February": 2,"March": 3,"April": 4,"May": 5,"June": 6,"July": 7,"August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    labels_days = range(1,32)
    values = getValue()
    count = 0
    data = range(1,13) 
    for key in labels:
    	data[count] = values[labels[key]]
    	count+=1
    labels = ["January","February","March","April","May","June","July","August", "September", "October", "November", "December"]
    
    data_days = range(1,32)
    count =0
    for day in labels_days:
    	data_days[count] = values[day]
    	count +=1




    # values = getValue() 
    # labels.sort()
    # labels= labels.sort()
    print data
    # print sorted(labels.items(), key =lambda x: x[1])


    labels2 = {"January": 1,"February": 2,"March": 3,"April": 4,"May": 5,"June": 6,"July": 7,"August": 8, "September": 9, "October": 10, "November": 11, "December": 12}    
    values2 = [10,9,8,7,6,4,7,8]

    labels3 = ["People Spotted","False Alarm"]
    values3 = [humanobjects,fpobjects]
    labels4 = {"January": 1,"February": 2,"March": 3,"April": 4,"May": 5,"June": 6,"July": 7,"August": 8, "September": 9, "October": 10, "November": 11, "December": 12}    
    values4 = [10,9,8,7,6,4,7,8]
    return render_template('chart.html', values=data_days, labels=labels_days,values2=values2, labels2=labels2,
    	values3=values3, labels3=labels3, values4=values4, labels4=labels4)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)