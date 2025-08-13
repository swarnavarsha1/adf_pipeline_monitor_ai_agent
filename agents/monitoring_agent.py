import time
import datetime
from config import PIPELINES_TO_MONITOR
from db_manager import DBManager

class MonitoringAgent:
    def __init__(self, adf_client, decision_agent):
        self.adf_client = adf_client
        self.decision_agent = decision_agent
        self.db = DBManager()

    def poll(self):
        print("[MonitoringAgent] Starting monitoring loop.")

        while True:
            # --- 1. Get failed/successful runs for monitored pipelines ---
            failed_runs = [r for r in self.adf_client.get_failed_pipelines()
                           if r['pipelineName'] in PIPELINES_TO_MONITOR]
            succeeded_runs = [r for r in self.adf_client.get_successful_pipelines()
                              if r['pipelineName'] in PIPELINES_TO_MONITOR]

            # --- 2. Reset retry records for successful runs ---
            for run in succeeded_runs:
                self.db.delete_run(run['pipelineName'], run['runId'])
                print(f"[MonitoringAgent] SUCCESS: {run['pipelineName']} run {run['runId']} -> Retry reset.")

            # --- 3. Process failed runs ---
            for run in failed_runs:
                p_name, orig_run_id = run['pipelineName'], run['runId']

                # Insert or ignore if already exists
                self.db.insert_run(p_name, orig_run_id, retry_count=2)
                info = self.db.get_run_info(p_name, orig_run_id)
                retries_left, last_attempt_id, status = (
                    info['retry_count'],
                    info['last_attempt_run_id'],
                    info['status']
                )

                # --- Case A: Last retry still running ---
                if status == "running" and last_attempt_id:
                    attempt_status = self.adf_client.get_pipeline_run_status(last_attempt_id)['status']
                    print(f"[MonitoringAgent] Last retry run {last_attempt_id} is {attempt_status}")
                    if attempt_status.lower() == "inprogress":
                        continue  # Wait until finished
                    elif attempt_status.lower() == "succeeded":
                        self.db.delete_run(p_name, orig_run_id)
                        print(f"[MonitoringAgent] Retry succeeded for {p_name} ({orig_run_id}). Reset.")
                        continue
                    elif attempt_status.lower() == "failed":
                        retries_left -= 1
                        self.db.update_retry(p_name, orig_run_id, retry_count=retries_left, status="pending")
                        print(f"[MonitoringAgent] Retry failed for {p_name} ({orig_run_id}). Retries left={retries_left}")
                        # If this was last retry, escalate now
                        if retries_left < 1:
                            self.decision_agent.notify_max_retries_exceeded(run, orig_run_id)
                        continue

                # --- Case B: No retries left ---
                if retries_left < 1:
                    self.decision_agent.notify_max_retries_exceeded(run, orig_run_id)
                    continue

                # --- Case C: Prompt for retry ---
                confirm = input(f"Run {orig_run_id} of {p_name} failed. Retry? (y/n): ").strip().lower()
                if confirm != 'y':
                    # Mark retries exhausted + escalate
                    self.db.update_retry(p_name, orig_run_id, retry_count=0)
                    self.decision_agent.notify_max_retries_exceeded(run, orig_run_id)
                    continue

                # --- Case D: AI Evaluation before retry ---
                ai_res = self.decision_agent.evaluate_failure(
                    pipeline_name=p_name,
                    activity=None,
                    error_message=run.get('message', ''),
                    run_id=orig_run_id
                )

                if ai_res is None:
                    # Notification was skipped because already sent
                    continue

                if ai_res['action'] == "none" or 'not recoverable' in ai_res['rationale'].lower():
                    self.db.update_retry(p_name, orig_run_id, retry_count=0)
                    self.decision_agent.notify_max_retries_exceeded(run, orig_run_id)
                    continue

                # --- Case E: Trigger actual retry ---
                outcome = self.decision_agent.trigger_rerun_agent.rerun(orig_run_id)

                if not outcome or 'runId' not in outcome:
                    print(f"[MonitoringAgent] ERROR: Rerun for {p_name} ({orig_run_id}) failed or returned invalid response: {outcome}")
                    # Mark as needing escalation if we cannot rerun
                    self.db.update_retry(p_name, orig_run_id, retry_count=0)
                    self.decision_agent.notify_max_retries_exceeded(run, orig_run_id)
                    continue

                new_retry_id = outcome.get('runId')

                self.db.update_retry(
                    p_name,
                    orig_run_id,
                    last_attempt_run_id=new_retry_id,
                    status="running"
                )

                print(f"[MonitoringAgent] Triggered retry #{3 - retries_left} for {p_name} ({orig_run_id}) as {new_retry_id}")


            # --- 4. Sleep until next poll ---
            sleep_seconds = 300  # 5 minutes
            wake_time = datetime.datetime.now() + datetime.timedelta(seconds=sleep_seconds)
            print(f"[MonitoringAgent] Polling complete. Sleeping for 5 minutes. "
                  f"Next check at {wake_time.strftime('%Y-%m-%d %H:%M:%S')}.\n")
            time.sleep(sleep_seconds)
