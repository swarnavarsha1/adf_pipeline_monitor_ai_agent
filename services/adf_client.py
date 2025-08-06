import requests
import datetime
from config import *

class AzureDataFactoryClient:
    def _get_token(self):
        print("[ADFClient] Fetching Azure AD token...")
        url = f"https://login.microsoftonline.com/{ADF_TENANT_ID}/oauth2/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': ADF_CLIENT_ID,
            'client_secret': ADF_CLIENT_SECRET,
            'resource': 'https://management.azure.com/'
        }
        res = requests.post(url, data=payload)
        res.raise_for_status()
        print("[ADFClient] Token received.")
        return res.json()["access_token"]

    def get_failed_pipelines(self):
        print("[ADFClient] Querying pipeline runs from ADF...")
        token = self._get_token()
        url = (f"https://management.azure.com/subscriptions/{ADF_SUBSCRIPTION_ID}/resourceGroups/"
               f"{ADF_RESOURCE_GROUP}/providers/Microsoft.DataFactory/factories/"
               f"{ADF_FACTORY_NAME}/queryPipelineRuns?api-version=2018-06-01")
        now = datetime.datetime.utcnow()
        filter_params = {
            "lastUpdatedAfter": (now - datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "lastUpdatedBefore": now.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        headers = {"Authorization": f"Bearer {token}"}
        try:
            res = requests.post(url, headers=headers, json=filter_params)
            res.raise_for_status()
            runs = res.json().get("value", [])
            failed = [run for run in runs if run["status"] == "Failed"]
            print(f"[ADFClient] {len(failed)} failed pipeline(s) detected in last hour.")
            return failed
        except Exception as e:
            print(f"[ADFClient] Error fetching pipeline runs: {e}")
            return []

    def rerun_pipeline(self, pipeline_name, start_activity=None):
        print(f"[ADFClient] Triggering rerun for pipeline: {pipeline_name}, start_activity: {start_activity}")
        token = self._get_token()
        url = (f"https://management.azure.com/subscriptions/{ADF_SUBSCRIPTION_ID}/resourceGroups/"
               f"{ADF_RESOURCE_GROUP}/providers/Microsoft.DataFactory/factories/"
               f"{ADF_FACTORY_NAME}/pipelines/{pipeline_name}/createRun?api-version=2018-06-01")
        body = {}
        if start_activity:
            body = {
                "isRecovery": True,
                "startActivityName": start_activity
            }
        headers = {"Authorization": f"Bearer {token}"}
        try:
            res = requests.post(url, headers=headers, json=body)
            res.raise_for_status()
            print("[ADFClient] Rerun triggered successfully.")
            return res.json()
        except Exception as e:
            print(f"[ADFClient] Error triggering rerun: {e}")
            return None
