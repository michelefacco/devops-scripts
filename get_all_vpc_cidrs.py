#!/opt/homebrew/bin/python3

import boto3

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

def action(region):
    print('--- {} ---'.format(region))
    clientEC2 = boto3.client('ec2', region_name = region)
    keep_going = True
    token = ''
    while keep_going:
        if token:
            response = clientEC2.describe_vpcs(NextToken = token)
        else:
            response = clientEC2.describe_vpcs()
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        for r in response['Vpcs']:
            print('VPC - {}'.format(r['VpcId']))
            if 'CidrBlockAssociationSet' in r:
                for a in r['CidrBlockAssociationSet']:
                    print(' > IPv4 = {}'.format(a['CidrBlock']))
            if 'Ipv6CidrBlockAssociationSet' in r:
                for a in r['Ipv6CidrBlockAssociationSet']:
                    print(' > IPv6 = {}'.format(a['Ipv6CidrBlock']))

for region in regions:
    try:
        action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
