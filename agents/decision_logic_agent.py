class DecisionLogicAgent:
    def __init__(self, openai_client, trigger_rerun_agent, notifier):
        self.openai_client = openai_client
        self.trigger_rerun_agent = trigger_rerun_agent
        self.notifier = notifier

    def evaluate_failure(self, pipeline_name, activity, error_message, run_id):
        print(f"[DecisionLogicAgent] Evaluating failure for pipeline: {pipeline_name}")
        ai_result = self.openai_client.ask_gpt(pipeline_name, activity, error_message)
        print(f"[DecisionLogicAgent] AI Decision: action={ai_result['action']}, rationale={ai_result['rationale']}")
        outcome = None
        if ai_result["action"] == "full":
            print(f"[DecisionLogicAgent] Triggering FULL rerun for pipeline '{pipeline_name}'.")
            outcome = self.trigger_rerun_agent.rerun(pipeline_name)
        elif ai_result["action"] == "partial":
            print(f"[DecisionLogicAgent] Triggering PARTIAL rerun for pipeline '{pipeline_name}' at activity '{activity}'.")
            outcome = self.trigger_rerun_agent.rerun(pipeline_name, activity=activity)
        else:
            print(f"[DecisionLogicAgent] No rerun triggered.")
        self.notifier.notify(pipeline_name, run_id, ai_result, outcome)
