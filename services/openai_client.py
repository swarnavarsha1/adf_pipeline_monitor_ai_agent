import openai
from config import OPENAI_API_KEY

class OpenAIClient:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY

    def ask_gpt(self, pipeline_name, activity, error_message):
        prompt = (f"Pipeline: {pipeline_name}\n"
                  f"Failed Activity: {activity}\n"
                  f"Error: {error_message}\n\n"
                  "Based on this, should we retry the full pipeline, just the failed activity, or not retry? "
                  "Reply with one word: 'full', 'partial', or 'none', then a rationale.")
        print(f"[OpenAIClient] Sending prompt to GPT-4 for pipeline '{pipeline_name}'...")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            reply = response.choices[0].message['content'].strip().lower()
            print(f"[OpenAIClient] GPT-4o replied: {reply}")
            action = "none"
            if "full" in reply:
                action = "full"
            elif "partial" in reply:
                action = "partial"
            elif "none" in reply:
                action = "none"
            return {"action": action, "rationale": reply}
        except Exception as e:
            print(f"[OpenAIClient] Error calling GPT-4: {e}")
            return {"action": "none", "rationale": "Error calling GPT-4"}
