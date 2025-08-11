# agents/trigger_rerun_agent.py
class TriggerRerunAgent:
    def __init__(self, adf_client):
        self.adf_client = adf_client

    def rerun(self, run_id):
        print(f"[TriggerRerunAgent] Triggering rerun for original runId={run_id}")
        outcome = self.adf_client.rerun_pipeline_by_run_id(run_id)
        print(f"[TriggerRerunAgent] Rerun started: {outcome}")
        return outcome
