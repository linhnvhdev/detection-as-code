import requests
import urllib3

urllib3.disable_warnings()

api_url_base="https://localhost:8089"
headers = {'Content-Type': 'application/json'}
auth_method="Splunk"
username="dungbacon"
password="devforlife011502"

def upload(rules):
    print("Upload to Splunk:\n")
    access_token = auth_method + " " + api_authorize() 
    api_upload_rules(rules, access_token)

def api_authorize():
    try:
        authorize_url = api_url_base + "/services/auth/login?output_mode=json"
        data = {'username': username, 'password': password}
        response = requests.post(authorize_url, headers=headers, data=data, verify=False)
        return response.json()['sessionKey']
    except:
        print("Error: cannot connect to Splunk")
        return None

def api_upload_rules(rules, access_token):
    try:
        auth_header={'Authorization': access_token}
        upload_url = api_url_base + "/services/search/jobs"

        for rule in rules:
            print("Search: " + rule.rule[0])
            response = requests.post(
                upload_url, 
                headers=auth_header, 
                data={
                    "search": "search " + rule.rule[0],
                }, 
                verify=False)
            print(response.text)
            print("\n")
            if(response.status_code == 201):
                print("Upload rule ", rule.title, " successfully")
            else:
                print("Error: cannot upload rule ", rule.title)
    except:
        print("Error: cannot connect to Splunk")
    
    