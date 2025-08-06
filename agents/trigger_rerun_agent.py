class TriggerRerunAgent:
    def __init__(self, adf_client):
        self.adf_client = adf_client

    def rerun(self, pipeline_name, activity=None):
        print(f"[TriggerRerunAgent] Requesting rerun for '{pipeline_name}', activity: {activity}")
        outcome = self.adf_client.rerun_pipeline(pipeline_name, start_activity=activity)
        if outcome:
            print(f"[TriggerRerunAgent] Rerun triggered! Response: {outcome}")
        else:
            print(f"[TriggerRerunAgent] Rerun failed or could not be triggered.")
        return outcome
