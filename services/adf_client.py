import requests
import datetime
from config import *

class AzureDataFactoryClient:
    def _get_token(self):
        """
        Authenticate with Azure AD to get a Bearer token for ADF REST API access.
        """
        print("[ADFClient] Fetching Azure AD token...")
        url = f"https://login.microsoftonline.com/{ADF_TENANT_ID}/oauth2/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': ADF_CLIENT_ID,
            'client_secret': ADF_CLIENT_SECRET,
            'resource': 'https://management.azure.com/'
        }
        try:
            res = requests.post(url, data=payload)
            res.raise_for_status()
            print("[ADFClient] Token received.")
            return res.json()["access_token"]
        except Exception as e:
            print(f"[ADFClient] Failed to obtain token: {e}")
            raise  # Re-raise since token is critical

    def get_failed_pipelines(self, hours=2):
        """
        Query ADF to get pipeline runs with status 'Failed' in the last `hours`.
        """
        print("[ADFClient] Querying failed pipeline runs from ADF...")
        token = self._get_token()
        url = (
            f"https://management.azure.com/subscriptions/{ADF_SUBSCRIPTION_ID}/resourceGroups/"
            f"{ADF_RESOURCE_GROUP}/providers/Microsoft.DataFactory/factories/"
            f"{ADF_FACTORY_NAME}/queryPipelineRuns?api-version=2018-06-01"
        )
        now = datetime.datetime.utcnow()
        filter_params = {
            "lastUpdatedAfter": (now - datetime.timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "lastUpdatedBefore": now.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        headers = {"Authorization": f"Bearer {token}"}
        try:
            res = requests.post(url, headers=headers, json=filter_params)
            res.raise_for_status()
            runs = res.json().get("value", [])
            failed = [run for run in runs if run.get("status") == "Failed"]
            print(f"[ADFClient] {len(failed)} failed pipeline(s) detected in last {hours} hours.")
            return failed
        except Exception as e:
            print(f"[ADFClient] Error fetching failed pipeline runs: {e}")
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return []

    def get_successful_pipelines(self, hours=2):
        """
        Query ADF to get pipeline runs with status 'Succeeded' in the last `hours`.
        """
        print("[ADFClient] Querying successful pipeline runs from ADF...")
        token = self._get_token()
        url = (
            f"https://management.azure.com/subscriptions/{ADF_SUBSCRIPTION_ID}/resourceGroups/"
            f"{ADF_RESOURCE_GROUP}/providers/Microsoft.DataFactory/factories/"
            f"{ADF_FACTORY_NAME}/queryPipelineRuns?api-version=2018-06-01"
        )
        now = datetime.datetime.utcnow()
        filter_params = {
            "lastUpdatedAfter": (now - datetime.timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "lastUpdatedBefore": now.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        headers = {"Authorization": f"Bearer {token}"}
        try:
            res = requests.post(url, headers=headers, json=filter_params)
            res.raise_for_status()
            runs = res.json().get("value", [])
            successful = [run for run in runs if run.get("status") == "Succeeded"]
            print(f"[ADFClient] {len(successful)} successful pipeline(s) detected in last {hours} hours.")
            return successful
        except Exception as e:
            print(f"[ADFClient] Error fetching successful pipeline runs: {e}")
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return []

    def rerun_pipeline(self, pipeline_name, start_activity=None):
        """
        Trigger a rerun of the specified pipeline.
        If start_activity is specified, trigger a partial rerun (recovery mode) from that activity.
        """
        print(f"[ADFClient] Triggering rerun for pipeline: {pipeline_name}, start_activity: {start_activity}")
        token = self._get_token()
        url = (
            f"https://management.azure.com/subscriptions/{ADF_SUBSCRIPTION_ID}/resourceGroups/"
            f"{ADF_RESOURCE_GROUP}/providers/Microsoft.DataFactory/factories/"
            f"{ADF_FACTORY_NAME}/pipelines/{pipeline_name}/createRun?api-version=2018-06-01"
        )
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
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return None
