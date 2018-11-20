#Upload pics to s3

import json
import boto3
import os

with open('/home/fiifi/Desktop/4813/PROJECT/IoTCamera/setup/aws_config/config.json') as aws_config:
	data = json.load(aws_config)

AWS_KEY= data.get('AWS_KEY', '')
AWS_SECRET= data.get('AWS_SECRET', '')
REGION = data.get('REGION', '')
BUCKET = data.get('BUCKET', '')

s3 = boto3.client('s3', aws_access_key_id=AWS_KEY,aws_secret_access_key=AWS_SECRET)



def uploadfile(path):
	files = os.listdir(path)
	full_dir = [os.path.join(path, basename) for basename in files]
	latest_file = max(full_dir, key=os.path.getctime)
	# Filename that will appear in S3. Strip the image number at the beginning of the file name
	# so filename starts with a date. For example 04-20170724114420-00.jpg becomes 20170724114420-00.jpg
	# The last two digits stand for the frame number.
	s3_filename = os.path.basename(latest_file)
	s3_filename = s3_filename[s3_filename.find('-')+1:]
	print("Uploading file {} to Amazon s3".format(s3_filename))
	s3.upload_file(latest_file, BUCKET, s3_filename, ExtraArgs={'ContentType': "image/jpeg", 'ACL': "public-read"})
	print("Removing file {}".format(latest_file))
	os.remove(latest_file)

uploadfile('/home/fiifi/s3pics')