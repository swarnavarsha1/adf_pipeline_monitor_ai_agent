import time

class MonitoringAgent:
    def __init__(self, adf_client, decision_agent):
        self.adf_client = adf_client
        self.decision_agent = decision_agent

    def poll(self):
        print("[MonitoringAgent] Starting monitoring loop. Press Ctrl+C to exit.")
        while True:
            print("[MonitoringAgent] Polling for failed pipelines...")
            failed_pipelines = self.adf_client.get_failed_pipelines()
            for run in failed_pipelines:
                print(f"[MonitoringAgent] Found failed pipeline: {run['pipelineName']} (Run ID: {run['runId']})")
                failed_activity = None
                error_message = "No error message."
                # Attempt to extract failed activity and error message
                if 'message' in run:
                    error_message = run['message']
                # If you get activityRuns from another API, you can try to extract more details here
                self.decision_agent.evaluate_failure(
                    pipeline_name=run["pipelineName"],
                    activity=failed_activity,
                    error_message=error_message,
                    run_id=run["runId"]
                )
            print("[MonitoringAgent] Polling complete. Sleeping for 2 minutes...\n")
            time.sleep(120)  # 2 minutes
