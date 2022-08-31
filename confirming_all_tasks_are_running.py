#!/opt/homebrew/bin/python3

import boto3

regions = ['us-west-1','us-west-2','us-east-1','us-east-2','af-south-1','ca-central-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3','eu-south-1','eu-north-1','me-south-1','sa-east-1','ap-east-1','ap-south-1','ap-southeast-1','ap-southeast-2','ap-southeast-3','ap-northeast-1','ap-northeast-2','ap-northeast-3']

clientSTS = boto3.client('sts')
account_id = clientSTS.get_caller_identity()['Account']
print('Detected Account ID = {}'.format(account_id))

def main_action(region):
    print('--- {} ---'.format(region))
    clientECS = boto3.client('ecs', region_name = region)
    action(clientECS)

def action(client, cluster = '', services = []):
    keep_going = True
    token = ''
    while keep_going:
        if services:
            response = client.describe_services(cluster = cluster, services = services)
        elif cluster:
            if token:
                response = client.list_services(cluster = cluster, NextToken = token)
            else:
                response = client.list_services(cluster = cluster)
        else:
            if token:
                response = client.list_clusters(NextToken = token)
            else:
                response = client.list_clusters()
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        if services:
            for s in response['services']:
                if s['desiredCount'] != s['runningCount']:
                    print('Task {} in cluster {} is having a difference between running and desired count'.format(s['serviceName'], cluster))
                td = client.describe_task_definition(taskDefinition=s['taskDefinition'])['taskDefinition']
                images = []
                for cd in td['containerDefinitions']:
                    images.append(cd['image'])
                for image in images:
                    if not account_id in image:
                        print('Image set to {} for service {}'.format(image, s['serviceName']))
        elif cluster:
            if response['serviceArns']:
                action(client, cluster = cluster, services = response['serviceArns'])
        else:
            for c in response['clusterArns']:
                action(client, cluster = c)

for region in regions:
    try:
        main_action(region)
    except Exception as e:
        print('Exception accessing region {}: {}'.format(region, e))
