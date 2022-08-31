#!/opt/homebrew/bin/python3

import boto3
import argparse

parser = argparse.ArgumentParser(description='Search deployed CF stacks for a specific resource. Multiple filters are handled with an AND logical operation.')
parser.add_argument('-t', '-tf', metavar='TYPE', help='Full match for the specified type of the AWS resource')
parser.add_argument('-tp', metavar='TYPE', help='Partial match for the specified type of the AWS resource, like *TYPE*')
parser.add_argument('-l', metavar='ID', help='Partial match for the specified AWS Logical ID')
parser.add_argument('-p', metavar='ID', help='Partial match for the specified AWS Physical ID')

args = parser.parse_args()

arg_t = vars(args)['t']
arg_tp = vars(args)['tp']
arg_l = vars(args)['l']
arg_p = vars(args)['p']

filter=['CREATE_COMPLETE','UPDATE_COMPLETE','UPDATE_ROLLBACK_COMPLETE']

clientCF = boto3.client('cloudformation')

def action(stack = ''):
    keep_going = True
    token = ''
    while keep_going:
        if stack:
            if token:
                response = clientCF.list_stack_resources(StackName = stack, NextToken = token)
            else:
                response = clientCF.list_stack_resources(StackName = stack)
        else:
            if token:
                response = clientCF.list_stacks(StackStatusFilter = filter, NextToken = token)
            else:
                response = clientCF.list_stacks(StackStatusFilter = filter)
        if 'NextToken' in response and response['NextToken']:
            token = response['NextToken']
        else:
            keep_going = False
        if stack:
            for r in response['StackResourceSummaries']:
                matches = True
                if arg_t:
                    if not arg_t == r['ResourceType']:
                        matches = False
                        continue
                if arg_tp:
                    if not arg_tp in r['ResourceType']:
                        matches = False
                        continue
                if arg_l:
                    if not arg_l in r['LogicalResourceId']:
                        matches = False
                        continue
                if arg_p:
                    if not arg_p in r['PhysicalResourceId']:
                        matches = False
                        continue
                if matches:
                    print('Resource {} {} {} found in stack {}'.format(r['LogicalResourceId'], r['PhysicalResourceId'], r['ResourceType'], stack))
        else:
            for s in response['StackSummaries']:
                action(s['StackName'])

action()
