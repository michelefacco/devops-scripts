#!/opt/homebrew/bin/python3

import json
import boto3
import argparse

parser = argparse.ArgumentParser(description='List all S3 related Event Bridge Rules.')
parser.add_argument('-a', '--all', action='store_true', help='Display even not S3 related rules')
args = parser.parse_args()

print_all = vars(args)['all']

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

def display(rule, source = '', detail = {}):
    print('Triggered rule found: {}'.format(rule['Name']))
    if 'Description' in rule and rule['Description']:
        print(' - Description: {}'.format(rule['Description'].strip()))
    if source:
        print(' - EventPatternSource: {}'.format(source))
    else:
        print(' - EventPatternSource not defined!')
    if detail:
        print('   - Details:')
        print('      > Bucket Name: {}'.format(detail['requestParameters']['bucketName']))
        if 'key' in detail['requestParameters'] and detail['requestParameters']['key']:
            print('      > Key: {}'.format(detail['requestParameters']['key']))
        print('      > Events: {}'.format(detail['eventName']))

def action(region):
    print('--- {} ---'.format(region))
    clientE = boto3.client('events', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientE.list_rules(NextToken = token)
        else:
            response = clientE.list_rules()
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        for rule in response['Rules']:
            if rule['State'] == 'ENABLED':
                if 'EventPattern' in rule and rule['EventPattern']:
                    event_pattern = json.loads(rule['EventPattern'])
                    if 'source' in event_pattern and event_pattern['source']:
                        is_s3_related = False
                        for s in event_pattern['source']:
                            if s == 'aws.s3':
                                is_s3_related = True
                        if is_s3_related:
                            display(rule, source = event_pattern['source'], detail = event_pattern['detail'])
                        else:
                            if print_all:
                                display(rule, source = event_pattern['source'])
                else:
                    if print_all:
                        display(rule)

for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
