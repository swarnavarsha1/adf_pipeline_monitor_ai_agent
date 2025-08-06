This project builds a smart **monitoring system for Azure Data Factory (ADF) pipelines** using OpenAI's GPT-4 AI:

- It regularly checks your data pipelines to see if they fail.
- When a failure happens, it sends details about the failure to GPT-4.
- GPT-4 analyzes the error message and decides if the pipeline should:
  - Fully rerun,
  - Partially rerun only the failed step,
  - Or not rerun at all.
- Based on AI’s decision, the system automatically triggers the required pipeline rerun via Azure API.
- It sends an email or alert with all this information to the operations team.

This turns your pipelines into a self-healing system — reducing downtime and manual work by automating failure detection and recovery with AI assistance.

# Simple Setup Instructions

1. **Prerequisites:**
   - Have an Azure subscription with Azure Data Factory set up.
   - Create an Azure Service Principal with permission to read and run pipelines.
   - Access to Azure OpenAI Service with GPT-4 enabled.
   - Install Python 3.8 or higher on your machine.

2. **Download the code:**

   Get the project folder onto your computer (you can copy it from the provided files or clone if available).

3. **Open in VS Code:**

   - Open Visual Studio Code.
   - Choose `File > Open Folder` and select the project folder (`adf_ai_pipeline_monitor`).

4. **Set up Python environment:**

   - Open a terminal in VS Code (`Terminal > New Terminal`).
   - Create and activate a virtual environment:

     ```bash
     python -m venv venv
     # On Windows
     venv\Scripts\activate
     # On macOS/Linux
     source venv/bin/activate
     ```

5. **Install required packages:**

   Run:

   ```bash
   pip install -r requirements.txt
   ```

6. **Configure credentials:**

   Open `config.py` and fill in your Azure and OpenAI credentials:

   ```python
   ADF_SUBSCRIPTION_ID = "your-azure-subscription-id"
   ADF_RESOURCE_GROUP = "your-azure-resource-group"
   ADF_FACTORY_NAME = "your-data-factory-name"
   ADF_TENANT_ID = "your-azure-tenant-id"
   ADF_CLIENT_ID = "your-service-principal-client-id"
   ADF_CLIENT_SECRET = "your-service-principal-client-secret"
   OPENAI_API_KEY = "your-openai-api-key"
   NOTIFICATION_EMAIL = "your-team-email@example.com"
   ```

7. **Run the monitoring system:**

   In the terminal, run:

   ```bash
   python main.py
   ```

   The system will start polling your ADF pipelines every 5 minutes, analyze failures with AI, rerun pipelines as needed, and notify you by printing alerts (extendable to email).
