# agents/notifier.py

from config import NOTIFICATION_EMAIL

class Notifier:
    def notify(self, pipeline_name, run_id, ai_result, rerun_outcome):
        """
        Standard notification with AI decision info.
        """
        subject = f"ADF Pipeline Failure and AI Action — {pipeline_name}"
        message = (
            f"Pipeline Run ID: {run_id}\n"
            f"AI Decision: {ai_result['action']}\n"
            f"Rationale: {ai_result['rationale']}\n"
            f"Rerun Outcome: {rerun_outcome}\n"
        )
        print(f"\n--- NOTIFICATION ---")
        print(f"TO: {NOTIFICATION_EMAIL}")
        print(f"SUBJECT: {subject}")
        print(message)
        print("--- END NOTIFICATION ---\n")
        # TODO: Implement actual sending via email or messaging service

    def notify_custom(self, pipeline_name, run_id, full_message):
        """
        Custom, fully formatted notification (e.g., enriched with RAG solution).
        This is now used by DecisionLogicAgent after AI evaluation.
        """
        subject = f"ADF Pipeline Failure — {pipeline_name}"
        print(f"\n--- CUSTOM NOTIFICATION ---")
        print(f"TO: {NOTIFICATION_EMAIL}")
        print(f"SUBJECT: {subject}")
        print(f"{full_message}")
        print("--- END CUSTOM NOTIFICATION ---\n")
        # TODO: Implement actual sending via email or messaging service
