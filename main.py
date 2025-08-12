from db_manager import DBManager
from agents.decision_logic_agent import DecisionLogicAgent
from agents.monitoring_agent import MonitoringAgent
from agents.notifier import Notifier
from agents.trigger_rerun_agent import TriggerRerunAgent
from services.openai_client import OpenAIClient
from services.adf_client import AzureDataFactoryClient

def main():
    print("[Main] Initializing agents and clients...")

    db_manager = DBManager()  # ✅ new
    notifier = Notifier()
    adf_client = AzureDataFactoryClient()
    openai_client = OpenAIClient()
    trigger_agent = TriggerRerunAgent(adf_client)
    decision_agent = DecisionLogicAgent(openai_client, trigger_agent, notifier, db_manager)
    monitoring_agent = MonitoringAgent(adf_client, decision_agent)
    
    print("[Main] Starting monitoring agent polling loop.")
    monitoring_agent.poll()

if __name__ == "__main__":
    main()
