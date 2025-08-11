# agents/decision_logic_agent.py
class DecisionLogicAgent:
    def __init__(self, openai_client, trigger_rerun_agent, notifier):
        self.openai_client = openai_client
        self.trigger_rerun_agent = trigger_rerun_agent
        self.notifier = notifier

    def evaluate_failure(self, pipeline_name, activity, error_message, run_id):
        print(f"[DecisionLogicAgent] Evaluating failure for {pipeline_name}, run {run_id}")
        ai_result = self.openai_client.ask_gpt(pipeline_name, activity, error_message)
        print(f"[DecisionLogicAgent] AI Decision = {ai_result}")

        outcome = None
        if ai_result['action'] in ("full", "partial"):
            outcome = self.trigger_rerun_agent.rerun(run_id)

        self.notifier.notify(pipeline_name, run_id, ai_result, outcome)
        return ai_result

    def notify_max_retries_exceeded(self, pipeline_run, run_id):
        pipeline_name = pipeline_run['pipelineName']
        subject = f"ADF Pipeline Retry Limit Exceeded — {pipeline_name}"
        message = f"Pipeline '{pipeline_name}' run '{run_id}' has exhausted retries.\nDetails: {pipeline_run}"
        self.notifier.notify_escalation(subject, message)
