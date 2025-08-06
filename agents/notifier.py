from config import NOTIFICATION_EMAIL

class Notifier:
    def notify(self, pipeline_name, run_id, ai_result, rerun_outcome):
        subject = f"ADF Pipeline Failure and AI Action — {pipeline_name}"
        message = (f"Pipeline Run ID: {run_id}\n"
                   f"AI Decision: {ai_result['action']}\n"
                   f"Rationale: {ai_result['rationale']}\n"
                   f"Rerun Outcome: {rerun_outcome}\n")
        print(f"\n--- NOTIFICATION ---")
        print(f"TO: {NOTIFICATION_EMAIL}")
        print(f"SUBJECT: {subject}")
        print(message)
        print("--- END NOTIFICATION ---\n")

    def notify_escalation(self, subject, message):
        print(f"\n--- ESCALATION ALERT ---")
        print(f"TO: {NOTIFICATION_EMAIL}")
        print(f"SUBJECT: {subject}")
        print(message)
        print("--- END ESCALATION ALERT ---\n")
        # TODO: Implement real email sending for escalation alert.
