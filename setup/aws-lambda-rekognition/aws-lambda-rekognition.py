from __future__ import print_function



import boto3
import json
import urllib



rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')
ses = boto3.client('ses')


# --------------- Helper Functions to call Rekognition APIs ------------------


def detect_faces(bucket, key):
    response = rekognition.detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response


def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response


def index_faces(bucket, key):
    response = rekognition.index_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}}, CollectionId="BLUEPRINT_COLLECTION")
    return response


# --------------- Main handler ------------------


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        # Calls rekognition DetectLabels API to detect labels in S3 object
        response_rekognition = detect_labels(bucket, key)

        # Print response to console.
        print(response_rekognition)

        # Detect human algorithm
        human_labels = ["Human", "People", "Person", "Selfie", "Face", "Portrait", "Child", "Kid"]
        human_detected = False
        for label in response_rekognition["Labels"]:
            if label["Name"] in human_labels and label["Confidence"] > 90:
                human_detected = True
                break

        #Detect weapons algorithm
        weapon_labels = ["Knife", "Gun", "Bomb", "Razor", "Scissors", "hammer", "Crowbar", "Hazard", "Sword", "Dagger"]
        weapon_detected = False
        for label in response_rekognition["Labels"]:
            if label["Name"] in weapon_labels and label["Confidence"] > 90:
                weapon_detected = True
                break



        # Move the image to the archive folder
        target_bucket = "raspcam-archive"
        target_key = "human/{}".format(key) if human_detected else "false_positive/{}".format(key)
        new_target_key = "weapons/{}".format(key) if weapon_detected and human_detected else "false_positive/{}".format(key)
        copy_source = {'Bucket':bucket, 'Key':key}
        response_s3 = s3.copy(Bucket=target_bucket, Key=target_key, CopySource=copy_source)
        response2_s3 = s3.copy(Bucket=target_bucket, Key=new_target_key, CopySource=copy_source)
        
        print(response_s3)
        print(response2_s3)
        response_s3 = s3.delete_object(Bucket=bucket, Key=key)
        response2_s3 = s3.delete_object(Bucket=bucket, Key=key)

        print(response2_s3)

        target_url = s3.generate_presigned_url('get_object', Params = {'Bucket': target_bucket, 'Key': target_key}, ExpiresIn = 24*3600)
        target2_url = s3.generate_presigned_url('get_object', Params = {'Bucket': target_bucket, 'Key': new_target_key}, ExpiresIn = 24*3600)
        print (target2_url)
        print(target_url)


        # Send e-mail notification for human
        if human_detected:
            email_from = "fiifikrampah2010@gmail.com"
            email_to = "fiifikrampah2010@gmail.com"
            response_ses = ses.send_email(
               Source = email_from,
                Destination={
                    'ToAddresses': [
                        email_to,
                     ],
                },
                Message={
                    'Subject': {
                        'Data': "Security Alert!! Motion of Human detected"
                    },
                    'Body': {
                        'Text': {
                            'Data': "Attention!! Motion has been detected by Camera!\nSee the attached image for further details.\n {}".format(target_url)
                        }
                    }
                }
            )
            print(response_ses)

        if weapon_detected and human_detected:
            email_from = "fiifikrampah2010@gmail.com"
            email_to = "fiifikrampah2010@gmail.com"
            response_ses = ses.send_email(
               Source = email_from,
                Destination={
                    'ToAddresses': [
                        email_to,
                     ],
                },
                Message={
                    'Subject': {
                        'Data': "Security Alert!! Motion of Human with weapon detected"
                    },
                    'Body': {
                        'Text': {
                            'Data': "Attention!! Motion has been detected by Camera!\nSee the attached image for further details.\n {}".format(target_url)
                        }
                    }
                }
            )
            print(response_ses)

        return response_rekognition

    except Exception as error:
        print(error)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise error
