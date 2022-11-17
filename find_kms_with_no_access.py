#!/opt/homebrew/bin/python3

import json
import boto3

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

def policies(client, key):
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response1 = client.list_key_policies(KeyId = key, Marker = token)
        else:
            response1 = client.list_key_policies(KeyId = key)
        if 'NextMarker' in response1 and response1['NextMarker']:
            token = response1['NextMarker']
        else:
            keep_going = False
        for r in response1['PolicyNames']:
            response2 = client.get_key_policy(KeyId = key, PolicyName = r)
            policy = json.loads(response2['Policy'])
            found = False
            for s in policy['Statement']:
                if 'Principal' in s:
                    if 'AWS' in s['Principal']:
                        if '{}:root'.format(account) in s['Principal']['AWS']:
                            found_a = False
                            found_r = False
                            if type(s['Action']) in (tuple, list):
                                for a in s['Action']:
                                    if 'kms:*' in a:
                                        found_a = True
                            else: 
                                if 'kms:*' in s['Action']:
                                    found_a = True
                            if type(s['Resource']) in (tuple, list):
                                for a in s['Resource']:
                                    if '*' in a:
                                        found_r = True
                            else: 
                                if '*' in s['Resource']:
                                    found_r = True
                            if found_a and found_r:
                                found = True
            if not found:
                print('Key: {}'.format(key))
                # print('Policy: {}'.format())


def action(region):
    print('--- {} ---'.format(region))
    clientKMS = boto3.client('kms', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response1 = clientKMS.list_keys(Marker = token)
        else:
            response1 = clientKMS.list_keys()
        if 'NextMarker' in response1 and response1['NextMarker']:
            token = response1['NextMarker']
        else:
            keep_going = False
        for r in response1['Keys']:
            response2 = clientKMS.describe_key(KeyId = r['KeyId'])
            # print(response2)
            if response2['KeyMetadata']['Enabled'] and 'Enabled' in response2['KeyMetadata']['KeyState'] and 'CUSTOMER' in response2['KeyMetadata']['KeyManager']:
                policies(clientKMS, r['KeyId'])

account = boto3.client('sts').get_caller_identity().get('Account')
print('Account ID detected: {}'.format(account))

for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
