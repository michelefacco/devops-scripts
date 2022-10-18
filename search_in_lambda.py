#!/opt/homebrew/bin/python3

import boto3
import zipfile
import argparse
import urllib.request

parser = argparse.ArgumentParser(description='List all Lambda Functions by partial name or by a value in either ENV or code.')
parser.add_argument('-name', help='Lookup name')
parser.add_argument('-value', help='Lookup value')
args = parser.parse_args()

name = vars(args)['name']
value = vars(args)['value']

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

def action(region):
    print('--- {} ---'.format(region))
    clientLAMBDA = boto3.client('lambda', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientLAMBDA.list_functions(Marker = token)
        else:
            response = clientLAMBDA.list_functions()
        if 'NextMarker' in response and response['NextMarker']:
            token = response['NextMarker']
        else:
            keep_going = False
        for function in response['Functions']:
            if name:
                if name.upper() in function['FunctionName'].upper():
                    print('Function: {}'.format(function['FunctionName']))
            if value:
                if 'Environment' in function:
                    if 'Variables' in function['Environment']:
                        for key in function['Environment']['Variables'].keys():
                            if value.upper() in key.upper() or value.upper() in function['Environment']['Variables'][key].upper():
                                print('Function: {} - ENV ( {} = {} )'.format(function['FunctionName'], key, function['Environment']['Variables'][key]))
                if 'nodejs' in function['Runtime'] or 'python' in function['Runtime']:
                    nested_response = clientLAMBDA.get_function(FunctionName = function['FunctionArn'])['Code']
                    if 'Location' in nested_response:
                        filehandle, _ = urllib.request.urlretrieve(nested_response['Location'])
                        with zipfile.ZipFile(filehandle, 'r') as zip_file_object:
                            for filename in zip_file_object.namelist():
                                if '/' not in filename:
                                    if '.py' in filename or '.js' in filename or '.json' in filename:
                                        with zip_file_object.open(filename) as file:
                                            content = str(file.read())
                                            if value.upper() in content.upper():
                                                print('Function: {} - FILE {}'.format(function['FunctionName'], filename))
                else:
                    print('Function: {} - Runtime {} is not supported by this script'.format(function['FunctionName'], function['Runtime']))

for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
