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


def api_get_searches(rule_title):
    try:
        session = requests.Session()
        session.auth = (username, password)
        session.verify = False
        searches_url = base_api_url + \
            f"/services/saved/searches/{rule_title}?output_mode=json"
        response = session.get(searches_url)
        if response.status_code == 404:
            return None
        else:
            data = response.json()['entry'][0]["name"]
            return data
    except Exception as err:
        print(err)
        return None


def api_upload_rules(rules, access_token):
    try:
        auth_header = {'Authorization': access_token}
        upload_url = base_api_url + "/services/saved/searches?output_mode=json"
        for rule in rules:
            if api_get_searches(rule.title) is not None:
                res = api_update_alert(rule.title, rule.rule[0])
                if res.status_code == 404:
                    print("Rule", rule.title, "not found")
                elif  res.status_code == 200:
                    print("Update rule", rule.title, "successfully")
                else :
                    print("Update rule", rule.title, "failed")
                continue
            schema = {
                "name": rule.title,
                "search": rule.rule[0],
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


def api_update_alert(rule_title, search):
    try:
        session = requests.Session()
        session.auth = (username, password)
        session.verify = False
        searches_url = base_api_url + \
            f"/services/saved/searches/{rule_title}?output_mode=json"
        response = session.post(searches_url, data={"search": search})

        return response
    except Exception as err:
        print(err)
        return None


def api_delete_search():
    pass
