class DecisionLogicAgent:
    def __init__(self, openai_client, trigger_rerun_agent, notifier):
        self.openai_client = openai_client
        self.trigger_rerun_agent = trigger_rerun_agent
        self.notifier = notifier

    def evaluate_failure(self, pipeline_name, activity, error_message, run_id, retry_manager):
        print(f"[DecisionLogicAgent] Evaluating failure for pipeline '{pipeline_name}' (Run ID: {run_id})")
        ai_result = self.openai_client.ask_gpt(pipeline_name, activity, error_message)
        print(f"[DecisionLogicAgent] AI Decision: action={ai_result['action']}, rationale={ai_result['rationale']}")
        outcome = None

        if ai_result["action"] == "full":
            print(f"[DecisionLogicAgent] Triggering FULL rerun for pipeline '{pipeline_name}'.")
            outcome = self.trigger_rerun_agent.rerun(pipeline_name)
            retry_manager.record_retry(pipeline_name, run_id)
        elif ai_result["action"] == "partial":
            print(f"[DecisionLogicAgent] Triggering PARTIAL rerun for pipeline '{pipeline_name}' at activity '{activity}'.")
            outcome = self.trigger_rerun_agent.rerun(pipeline_name, activity=activity)
            retry_manager.record_retry(pipeline_name, run_id)
        else:
            print(f"[DecisionLogicAgent] No rerun triggered.")

        self.notifier.notify(pipeline_name, run_id, ai_result, outcome)

    def notify_max_retries_exceeded(self, pipeline_run, run_id):
        pipeline_name = pipeline_run['pipelineName']
        subject = f"ADF Pipeline Retry Limit Exceeded — {pipeline_name}"
        message = (
            f"Pipeline Run ID: {run_id}\n"
            f"The pipeline '{pipeline_name}' has failed repeatedly and reached the maximum retry limit.\n"
            f"Manual intervention is required.\n"
            f"Failure details: {pipeline_run}\n"
        )
        print(f"[DecisionLogicAgent] Sending escalation notification for pipeline '{pipeline_name}', run {run_id}")
        self.notifier.notify_escalation(subject, message)
