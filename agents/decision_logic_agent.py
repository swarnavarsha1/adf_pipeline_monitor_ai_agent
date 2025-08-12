# agents/decision_logic_agent.py

import datetime
from rag.rag_solution_retriever import RAGSolutionRetriever

class DecisionLogicAgent:
    def __init__(self, openai_client, trigger_rerun_agent, notifier, db_manager):
        self.openai_client = openai_client
        self.trigger_rerun_agent = trigger_rerun_agent
        self.notifier = notifier
        self.db = db_manager
        self.rag = RAGSolutionRetriever()

    def evaluate_failure(self, pipeline_name, activity, error_message, run_id, escalation_needed=False):
        run_info = self.db.get_run_info(pipeline_name, run_id)

        # Check if notification already sent for this failure
        if run_info and run_info.get("notified") == 1:
            print(f"[DecisionLogicAgent] Notification already sent for {pipeline_name} ({run_id}) - skipping send.")
            return None

        print(f"[DecisionLogicAgent] Evaluating failure for pipeline '{pipeline_name}', run ID: {run_id}")

        ai_result = self.openai_client.ask_gpt(pipeline_name, activity, error_message)
        failure_rationale = ai_result.get('rationale', '').strip()

        print(f"[DecisionLogicAgent] AI Action: {ai_result['action']}")
        print(f"[DecisionLogicAgent] AI Rationale: {failure_rationale}")

        rag_solution = self.rag.get_solution(failure_rationale) if failure_rationale else "No documented solution found."
        if rag_solution:
            print(f"[DecisionLogicAgent] Retrieved solution from KB:\n{rag_solution}")

        rerun_outcome = None
        if ai_result['action'] in ("full", "partial"):
            rerun_outcome = self.trigger_rerun_agent.rerun(run_id)

        # Compose single notification message
        notification_message = (
            f"Pipeline: {pipeline_name}\n"
            f"Run ID: {run_id}\n"
            f"AI Decision: {ai_result['action']}\n"
            f"Rationale:\n{failure_rationale}\n\n"
            f"--- Suggested Solution from Knowledge Base ---\n{rag_solution}\n"
        )

        if rerun_outcome:
            notification_message += f"\nRerun Outcome: {rerun_outcome}\n"

        if escalation_needed:
            notification_message += "\n--- ESCALATION REQUIRED ---\nRetry limit exceeded, manual intervention needed.\n"

        # Send notification
        self.notifier.notify_custom(pipeline_name, run_id, notification_message)

        # Mark as notified
        self.db.update_retry(
            pipeline_name,
            run_id,
            notified=1,
            last_notification_time=datetime.datetime.utcnow().isoformat()
        )

        return ai_result

    def notify_max_retries_exceeded(self, pipeline_run, run_id):
        pipeline_name = pipeline_run['pipelineName']
        error_message = pipeline_run.get('message', 'No error message provided.')
        self.evaluate_failure(pipeline_name, None, error_message, run_id, escalation_needed=True)
