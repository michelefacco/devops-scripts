#!/opt/homebrew/bin/python3

import boto3
import argparse
from datetime import datetime as dt

parser = argparse.ArgumentParser(description='Search update CF stacks for a specific date.')
parser.add_argument('-d', '-date', metavar='TYPE', help='Date that must match, in the format YYYY-MM-DD')

args = parser.parse_args()

td = vars(args)['d'].split('-')
converted_date = dt(int(td[0]),int(td[1]),int(td[2])).date()

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

filter=['UPDATE_COMPLETE']

def action(region):
    print('--- {} ---'.format(region))
    clientCF = boto3.client('cloudformation', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientCF.list_stacks(StackStatusFilter = filter, NextToken = token)
        else:
            response = clientCF.list_stacks(StackStatusFilter = filter)
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        for r in response['StackSummaries']:
            if converted_date == r['LastUpdatedTime'].date():
                print('Changes detected for stack {} at {}'.format(r['StackName'], r['LastUpdatedTime']))
                    
for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
