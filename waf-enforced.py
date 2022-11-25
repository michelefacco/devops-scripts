#!/opt/homebrew/bin/python3

import boto3
import argparse

parser = argparse.ArgumentParser(description='Enable WAF enforced rules (NOTE: This will impact customers).')
parser.add_argument('-e', '--enable', action='store_true', help='Enable the enforcement, run it without this option to disable it!')
args = parser.parse_args()

enableSwitch = vars(args)['enable']

disable = True

if enableSwitch:
    disable = False

regionList                    = ['us-east-1', 'us-west-1', 'us-west-2', 'ap-southeast-2', 'eu-central-1', 'eu-west-1']
listOfRuleWithAWSManagedRules = ['CrossSiteScripting_BODY', 'CrossSiteScripting_COOKIE', 'CrossSiteScripting_QUERYARGUMENTS', 'CrossSiteScripting_URIPATH', 'EC2MetaDataSSRF_BODY', 'EC2MetaDataSSRF_COOKIE', 'EC2MetaDataSSRF_QUERYARGUMENTS', 'EC2MetaDataSSRF_URIPATH', 'GenericLFI_BODY', 'GenericLFI_QUERYARGUMENTS', 'GenericLFI_URIPATH', 'GenericRFI_BODY', 'GenericRFI_QUERYARGUMENTS', 'GenericRFI_URIPATH', 'NoUserAgent_HEADER', 'RestrictedExtensions_QUERYARGUMENTS', 'RestrictedExtensions_URIPATH', 'SizeRestrictions_BODY', 'SizeRestrictions_Cookie_HEADER', 'SizeRestrictions_QUERYSTRING', 'SizeRestrictions_URIPATH', 'UserAgent_BadBots_HEADER']

for region in regionList:
    print('--- Region: {} ---'.format(region))
    client = boto3.client('wafv2', region_name = region)
    nextToken = ''
    keepGoing = True
    while keepGoing:
        keepGoing = False
        if nextToken:
            response = client.list_web_acls(Scope = 'REGIONAL', NextMarker = nextToken)
        else:
            response = client.list_web_acls(Scope = 'REGIONAL')
        if 'NextMarker' in response:
            keepGoing = True
            nextToken = response['NextMarker']
        for acl in response['WebACLs']:
            lockToken = acl['LockToken']
            if 'email-risk-score-' in acl['Name']:
                print('> {}'.format(acl['Name']))
                response = client.get_web_acl(Name = acl['Name'], Scope = 'REGIONAL', Id = acl['Id'])['WebACL']
                for rule in response['Rules']:
                    if 'DDOSBlock' == rule['Name']:
                        if disable:
                            rule['Action'] = {'Count': {}}
                        else:
                            rule['Action'] = {'Block': {}}
                    elif 'BlockedIPs' == rule['Name']:
                        if disable:
                            rule['Action'] = {'Count': {}}
                        else:
                            rule['Action'] = {'Block': {}}
                    elif 'RuleWithAWSManagedRules' == rule['Name']:
                        rule['Statement']['ManagedRuleGroupStatement']['ExcludedRules'] = []
                        rule['Statement']['ManagedRuleGroupStatement']['RuleActionOverrides'] = []
                        for action in listOfRuleWithAWSManagedRules:
                            if 'NoUserAgent_HEADER' != action:
                                if disable:
                                    rule['Statement']['ManagedRuleGroupStatement']['RuleActionOverrides'].append({'Name': action, 'ActionToUse': {'Count': {}}})
                                else:
                                    rule['Statement']['ManagedRuleGroupStatement']['RuleActionOverrides'].append({'Name': action, 'ActionToUse': {'Block': {}}})
                            else:
                                rule['Statement']['ManagedRuleGroupStatement']['RuleActionOverrides'].append({'Name': action, 'ActionToUse': {'Allow': {}}})
                    elif 'sebastian-p1-attack-rate-based' == rule['Name']:
                        if disable:
                            rule['Statement']['RateBasedStatement']['Limit'] = 5000
                        else:
                            rule['Statement']['RateBasedStatement']['Limit'] = 3000
                client.update_web_acl(Name = acl['Name'], Scope = 'REGIONAL', Id = acl['Id'], DefaultAction = response['DefaultAction'], Rules = response['Rules'], VisibilityConfig = response['VisibilityConfig'], LockToken = lockToken)
            elif 'portal3-' in acl['Name']:
                print('> {}'.format(acl['Name']))
                response = client.get_web_acl(Name = acl['Name'], Scope = 'REGIONAL', Id = acl['Id'])['WebACL']
                for rule in response['Rules']:
                    if 'RuleWithAWSManagedRules' == rule['Name']:
                        rule['Statement']['ManagedRuleGroupStatement']['ExcludedRules'] = []
                        rule['Statement']['ManagedRuleGroupStatement']['RuleActionOverrides'] = []
                        for action in listOfRuleWithAWSManagedRules:
                            if 'NoUserAgent_HEADER' != action:
                                if disable:
                                    rule['Statement']['ManagedRuleGroupStatement']['RuleActionOverrides'].append({'Name': action, 'ActionToUse': {'Count': {}}})
                                else:
                                    rule['Statement']['ManagedRuleGroupStatement']['RuleActionOverrides'].append({'Name': action, 'ActionToUse': {'Block': {}}})
                            else:
                                rule['Statement']['ManagedRuleGroupStatement']['RuleActionOverrides'].append({'Name': action, 'ActionToUse': {'Allow': {}}})
                client.update_web_acl(Name = acl['Name'], Scope = 'REGIONAL', Id = acl['Id'], DefaultAction = response['DefaultAction'], Rules = response['Rules'], VisibilityConfig = response['VisibilityConfig'], LockToken = lockToken)
print('Done!')
