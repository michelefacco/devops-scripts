#!/opt/homebrew/bin/python3

import boto3
import argparse

parser = argparse.ArgumentParser(description='List CF stacks by name and print out their resources.')
parser.add_argument('name', help='Lookup name')
args = parser.parse_args()

name = vars(args)['name']

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

filter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']

def details(client, stack):
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = client.list_stack_resources(StackName = stack, NextToken = token)
        else:
            response = client.list_stack_resources(StackName = stack)
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        for resource in response['StackResourceSummaries']:
            print('   - Logical: {} \t\t Physical: {} \t\t Type: {}'.format(resource['LogicalResourceId'], resource['PhysicalResourceId'], resource['ResourceType']))

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
        for stack in response['StackSummaries']:
            if name.upper() in stack['StackName'].upper():
                print(' > Stack: {}'.format(stack['StackName']))
                details(clientCF, stack['StackName'])
                    
for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
