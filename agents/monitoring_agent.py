import time
from retry_manager import RetryManager

class MonitoringAgent:
    def __init__(self, adf_client, decision_agent):
        self.adf_client = adf_client
        self.decision_agent = decision_agent
        self.retry_manager = RetryManager(max_retries=2)

    def poll(self):
        print("[MonitoringAgent] Starting monitoring loop. Press Ctrl+C to exit.")
        while True:
            print("[MonitoringAgent] Polling for failed pipelines...")
            
            failed_pipelines = self.adf_client.get_failed_pipelines()
            successful_pipelines = self.adf_client.get_successful_pipelines()

            # Collect pipeline names with recent successes
            successful_pipeline_names = set(run['pipelineName'] for run in successful_pipelines)

            for run in failed_pipelines:
                pipeline_name = run['pipelineName']
                run_id = run['runId']

                # Skip retry if pipeline has succeeded recently
                if pipeline_name in successful_pipeline_names:
                    if (pipeline_name, run_id) in self.retry_manager.retry_counts or \
                       (pipeline_name, run_id) in self.retry_manager.blocked_runs:
                        print(f"[MonitoringAgent] Resetting retries for pipeline '{pipeline_name}', run '{run_id}' due to success.")
                        self.retry_manager.reset_retry(pipeline_name, run_id)
                    print(f"[MonitoringAgent] Skipping retry for succeeded pipeline '{pipeline_name}', run '{run_id}'.")
                    continue

                # Check retry threshold
                if not self.retry_manager.can_retry(pipeline_name, run_id):
                    print(f"[MonitoringAgent] Max retries exceeded for pipeline '{pipeline_name}', run '{run_id}'. Sending escalation alert.")
                    self.decision_agent.notify_max_retries_exceeded(run, run_id)
                    continue

                print(f"[MonitoringAgent] Found failed pipeline: {pipeline_name} (Run ID: {run_id})")
                
                self.decision_agent.evaluate_failure(
                    pipeline_name=pipeline_name,
                    activity=None,
                    error_message=run.get('message', 'No error message.'),
                    run_id=run_id,
                    retry_manager=self.retry_manager
                )

            print("[MonitoringAgent] Polling complete. Sleeping for 5 minutes...\n")
            time.sleep(300)  # 5 minutes
