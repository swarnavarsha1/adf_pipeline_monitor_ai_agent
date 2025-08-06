from services.adf_client import AzureDataFactoryClient
from services.openai_client import OpenAIClient
from agents.monitoring_agent import MonitoringAgent
from agents.decision_logic_agent import DecisionLogicAgent
from agents.trigger_rerun_agent import TriggerRerunAgent
from agents.notifier import Notifier

def main():
    print("[Main] Initializing agents and clients...")
    adf_client = AzureDataFactoryClient()
    openai_client = OpenAIClient()
    notifier = Notifier()
    trigger_agent = TriggerRerunAgent(adf_client)
    decision_agent = DecisionLogicAgent(openai_client, trigger_agent, notifier)
    monitoring_agent = MonitoringAgent(adf_client, decision_agent)

    print("[Main] Starting monitoring agent polling loop.")
    monitoring_agent.poll()

if __name__ == "__main__":
    main()
