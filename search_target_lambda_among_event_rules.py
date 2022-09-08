#!/opt/homebrew/bin/python3

import json
import boto3
import argparse

parser = argparse.ArgumentParser(description='List all Event Bridge Rules that targets a specific lambda ARN.')
parser.add_argument('target', help='Target lambda ARN')
args = parser.parse_args()

target = vars(args)['target']

# account_id = boto3.client('sts').get_caller_identity().get('Account')

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

def action(region):
    print('--- {} ---'.format(region))
    clientE = boto3.client('events', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientE.list_rule_names_by_target(TargetArn = target, NextToken = token)
        else:
            response = clientE.list_rule_names_by_target(TargetArn = target)
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        if response['RuleNames']:
            print(response['RuleNames'])
                   
for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
