import requests
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings()

auth_method = os.getenv('SPLUNK_AUTH_PRE')
username = os.getenv('SPLUNK_USERNAME')
password = os.getenv('SPLUNK_PASSWORD')
base_api_url = os.getenv('SPLUNK_URL_BASE')


def upload(rules):
    print("Upload to Splunk:\n")
    print(api_authorize())
    access_token = auth_method + " " + api_authorize()
    api_upload_rules(rules, access_token)
    # api_search_job(rules, access_token)


def api_authorize():
    try:
        headers = {'Content-Type': 'application/json'}
        authorize_url = base_api_url + "/services/auth/login?output_mode=json"
        data = {'username': username, 'password': password}
        response = requests.post(
            authorize_url, headers=headers, data=data, verify=False)
        return response.json()['sessionKey']
    except:
        print("Error: cannot connect to Splunk")
        return None


def api_upload_rules(rules, access_token):
    try:
        auth_header = {'Authorization': access_token}
        upload_url = base_api_url + "/services/saved/searches?output_mode=json"
        for rule in rules:
            schema = {
                "name": rule.title,
                "search": "index=main eventtype=ms-sysmon-process",
                "is_scheduled": True,
                "cron_schedule": "*/5 * * * *",
                "alert_type": "number of events",
                "alert_comparator": "greater than",
                "alert_threshold": 5,
            }
            response = requests.post(
                upload_url,
                headers=auth_header,
                data=schema,
                verify=False
            )
            if (response.status_code == 201):
                print("Upload rule", rule.title, "successfully")
            else:
                print("Upload rule", rule.title, "failed")

    except Exception as err:
        print(err)


def api_search_job(rules, access_token):
    try:
        auth_header = {'Authorization': access_token}
        upload_url = base_api_url + "/services/search/jobs?output_mode=json"
        # for rule in rules:
        if True:
            schema = {
                "name": "test-real-time",
                "search": "search index=main eventtype=ms-sysmon-process",
                "search_mode": "realtime",
                "indexedRealtime": 1,
                "indexedRealtimeOffset": 300,
            }

            response = requests.post(
                upload_url,
                headers=auth_header,
                data=schema,
                verify=False
            )
            if (response.status_code == 201):
                print("Upload rule", "test-real-time", " successfully")
            else:
                print(response.content)
    except Exception as err:
        print(err)


def api_update_search():
    pass


def api_delete_search():
    pass
