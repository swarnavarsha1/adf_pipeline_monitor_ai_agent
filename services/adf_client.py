import requests
import datetime
from config import ADF_SUBSCRIPTION_ID, ADF_RESOURCE_GROUP, ADF_FACTORY_NAME, ADF_TENANT_ID, \
    ADF_CLIENT_ID, ADF_CLIENT_SECRET, PIPELINES_TO_MONITOR


class AzureDataFactoryClient:
    def _get_token(self):
        """
        Authenticate with Azure AD to get Bearer token for ADF REST API access.
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
            raise  # re-raise since token is required

    def get_failed_pipelines(self, hours=2):
        """
        Query ADF for failed pipeline runs in the last `hours`.
        Returns ONLY those in PIPELINES_TO_MONITOR.
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
            failed = [
                run for run in runs
                if run.get("status") == "Failed"
                and run.get("pipelineName") in PIPELINES_TO_MONITOR
            ]
            print(f"[ADFClient] {len(failed)} failed pipeline(s) detected in last {hours} hour(s) "
                  f"(filtered to monitored pipelines).")
            return failed
        except Exception as e:
            print(f"[ADFClient] Error fetching failed pipeline runs: {e}")
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return []

    def get_successful_pipelines(self, hours=2):
        """
        Query ADF for succeeded pipeline runs in the last `hours`.
        Returns ONLY those in PIPELINES_TO_MONITOR.
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
            succeeded = [
                run for run in runs
                if run.get("status") == "Succeeded"
                and run.get("pipelineName") in PIPELINES_TO_MONITOR
            ]
            print(f"[ADFClient] {len(succeeded)} successful pipeline(s) detected in last {hours} hour(s) "
                  f"(filtered to monitored pipelines).")
            return succeeded
        except Exception as e:
            print(f"[ADFClient] Error fetching successful pipeline runs: {e}")
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return []

    def rerun_pipeline(self, pipeline_name, start_activity=None):
        """
        Start a NEW pipeline run by its name (not tied to a specific failed run).
        Useful for fresh runs, not for retrying failed runs.
        """
        print(f"[ADFClient] Triggering pipeline '{pipeline_name}' (start_activity={start_activity})...")
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
            print("[ADFClient] Pipeline run started successfully.")
            return res.json()
        except Exception as e:
            print(f"[ADFClient] Error starting pipeline: {e}")
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return None

    def rerun_pipeline_by_run_id(self, run_id):
        """
        Trigger a rerun of a specific failed run (ADF Monitor -> Rerun equivalent).
        This uses the original runId and creates a new one for the rerun.
        """
        print(f"[ADFClient] Triggering rerun from monitor for runId={run_id}...")
        token = self._get_token()
        url = (
            f"https://management.azure.com/subscriptions/{ADF_SUBSCRIPTION_ID}/resourceGroups/"
            f"{ADF_RESOURCE_GROUP}/providers/Microsoft.DataFactory/factories/"
            f"{ADF_FACTORY_NAME}/pipelineruns/{run_id}/rerun?api-version=2018-06-01"
        )
        headers = {"Authorization": f"Bearer {token}"}
        try:
            res = requests.post(url, headers=headers)
            res.raise_for_status()
            print("[ADFClient] Monitor rerun triggered successfully.")
            return res.json()  # returns {"runId": "..."} for new run
        except Exception as e:
            print(f"[ADFClient] Error rerunning pipeline run by run_id: {e}")
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return None

    def get_pipeline_run_status(self, run_id):
        """
        Get current status of a specific pipeline run.
        """
        token = self._get_token()
        url = (
            f"https://management.azure.com/subscriptions/{ADF_SUBSCRIPTION_ID}/resourceGroups/"
            f"{ADF_RESOURCE_GROUP}/providers/Microsoft.DataFactory/factories/"
            f"{ADF_FACTORY_NAME}/pipelineruns/{run_id}?api-version=2018-06-01"
        )
        headers = {"Authorization": f"Bearer {token}"}
        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            return res.json()  # contains 'status': 'InProgress'|'Failed'|'Succeeded'
        except Exception as e:
            print(f"[ADFClient] Error checking run status for runId {run_id}: {e}")
            if hasattr(e, 'response'):
                print(f"Response content: {e.response.text}")
            return None
