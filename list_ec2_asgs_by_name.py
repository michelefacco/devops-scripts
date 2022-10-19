#!/opt/homebrew/bin/python3

import boto3
import argparse

parser = argparse.ArgumentParser(description='List EC2 and AutoScalingGroups by partial name matching.')
parser.add_argument('name', help='Lookup name')
args = parser.parse_args()

name = vars(args)['name']

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

filter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']

def action(region):
    print('--- {} ---'.format(region))
    clientEC2 = boto3.client('ec2', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientEC2.describe_instances(Filters = [{'Name':'tag-key','Values':['Name']}], NextToken = token)
        else:
            response = clientEC2.describe_instances(Filters = [{'Name':'tag-key','Values':['Name']}])
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                for tag in instance['Tags']:
                    if 'Name' in tag['Key']:
                        if name.upper() in tag['Value'].upper():
                            print(' > Instance: {} ({})'.format(instance['InstanceId'], tag['Value']))
    clientASG = boto3.client('autoscaling', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientASG.describe_auto_scaling_groups(NextToken = token)
        else:
            response = clientASG.describe_auto_scaling_groups()
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        for asg in response['AutoScalingGroups']:
            if name.upper() in asg['AutoScalingGroupName'].upper():
                print(' > ASG: {}'.format(asg['AutoScalingGroupName']))
                
for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
