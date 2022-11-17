#!/opt/homebrew/bin/python3

import boto3

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

clientS3 = boto3.client('s3')
response = clientS3.list_buckets()
for r in response['Buckets']:
    try:
        clientS3.get_bucket_location(Bucket = r['Name'])['LocationConstraint']
    except:
        print('Error accessing location details for bucket: {}'.format(r['Name']))
