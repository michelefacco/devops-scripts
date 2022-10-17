#!/opt/homebrew/bin/python3

import boto3
import argparse

parser = argparse.ArgumentParser(description='List all SSM Parameters and Secret Manager secrets by partial name or partial value.')
parser.add_argument('-name', help='Lookup name')
parser.add_argument('-value', help='Lookup value')
args = parser.parse_args()

name = vars(args)['name']
value = vars(args)['value']

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

def action(region):
    print('--- {} ---'.format(region))
    clientSSM = boto3.client('ssm', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientSSM.describe_parameters(NextToken = token)
        else:
            response = clientSSM.describe_parameters()
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        for param in response['Parameters']:
            if name:
                if name.upper() in param['Name'].upper():
                    print('Parameter: {}'.format(param['Name']))
            if value:
                nested_response = clientSSM.get_parameter(Name = param['Name'], WithDecryption = True)['Parameter']['Value']
                if value.upper() in nested_response.upper():
                    print('Parameter: {} = {}'.format(param['Name'], nested_response))
    clientSM = boto3.client('secretsmanager', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientSM.list_secrets(NextToken = token)
        else:
            response = clientSM.list_secrets()
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        for secret in response['SecretList']:
            if name:
                if name.upper() in secret['Name'].upper():
                    print('Secret: {}'.format(secret['Name']))
            if value:
                nested_response = clientSM.get_secret_value(SecretId = secret['ARN'])['SecretString']
                if value.upper() in nested_response.upper():
                    print('Secret: {} = {}'.format(secret['Name'], nested_response))
                   
for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
