import requests
import subprocess
import json
import os 
from dotenv import load_dotenv

def upload(rules):
    print("Upload to Sentinel")
    bearer_token = login_to_azure()
    upload_rules(rules, bearer_token)

def login_to_azure():
    load_dotenv()
    try:
        login_command = f"az login --service-principal -u {os.getenv('APP_ID')} -p {os.getenv('SP_PASSWORD')} --tenant {os.getenv('TENANT')}"
        login_process = subprocess.call(login_command, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        #login_process = subprocess.call(login_command, shell=True)
        get_token_process = subprocess.check_output("az account get-access-token --output json", shell=True, stderr=subprocess.DEVNULL)
        token_data = json.loads(get_token_process)
        bearer_token = token_data['accessToken']
        print("Login to azure successfully")
        return bearer_token
    except:
        print("Login to azure unsuccessfully. Please check your credentials or internet connection")
        return None

def format_rule(rule):
    if rule.severity == "CRITICAL" or rule.severity == "HIGH":
        corrected_rule = {
            'kind': "NRT",
            'properties' : {
                'displayName': rule.title,
                'enabled': True,
                'query': rule.rule[0],
                'severity': "High",
                'suppressionDuration' : "PT1H",
                'suppressionEnabled': False,
            }     
        }
        return json.dumps(corrected_rule)
    else :
        corrected_rule = {
            'kind': "Scheduled",
            'properties' : {
                'displayName': rule.title,
                'enabled': True,
                'query': rule.rule[0],
                'severity': rule.severity,
                "queryFrequency": "PT1H",
                "queryPeriod": "P2DT1H30M",
                "triggerOperator": "GreaterThan",
                "triggerThreshold": 0,
                "suppressionDuration": "PT1H",
                "suppressionEnabled": False,
            }     
        }
        return json.dumps(corrected_rule)

def upload_rules(rules, bearer_token):
    if bearer_token == None: return
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    for rule in rules:
        corrected_rule = format_rule(rule)
        try:
            rule_url = f"https://management.azure.com/subscriptions/{os.getenv('SUBSCRIPTION_ID')}/resourceGroups/{os.getenv('RESOURCE_GROUP_NAME')}/providers/Microsoft.OperationalInsights/workspaces/{os.getenv('WORKSPACE_NAME')}/providers/Microsoft.SecurityInsights/alertRules/{rule.id}?api-version=2023-07-01-preview" 
            upload_request = requests.put(rule_url,headers=headers,data=corrected_rule)
            if upload_request.status_code == 200 or upload_request.status_code == 201:
                print("Upload successfully rule ", rule.id)
            else:
                print("Upload unsuccessfully rule ", rule.id, "Status code: ", upload_request.status_code)
        except:
            print("Something went wrong. Upload unsuccessfully rule ", rule.id)

