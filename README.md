# ADF AI Pipeline Monitor

This project implements a smart **AI-powered monitoring system for Azure Data Factory (ADF) pipelines** using OpenAI’s GPT-4. It helps you:

- Automatically detect when ADF pipelines fail.
- Send failure details to GPT-4 for intelligent analysis.
- Let GPT-4 decide whether to rerun the full pipeline, rerun just the failed part, or skip rerun.
- Automatically trigger pipeline reruns based on AI decisions.
- Notify your team via email or console alerts about failures and actions taken.

This makes your data pipelines more resilient and reduces manual troubleshooting.


## Features

- Continuous, near-real-time failure monitoring of ADF pipelines.
- AI-driven decision making with GPT-4 for intelligent recovery.
- Automated pipeline reruns (full or partial).
- RAG integration — retrieves relevant solutions from your own PDF knowledge base and includes them in notifications
- Notification support via email
- Modular architecture for easy customization.


## Prerequisites

- Azure subscription with Azure Data Factory pipelines.
- Azure Service Principal with rights to read/run pipelines.
- Access to Azure OpenAI service with GPT-4 enabled.
- Python 3.8 or newer.
- (Optional) SMTP email account credentials for notifications.


## Simple Setup Instructions

1. **Clone the repository:**

    ```
    git clone https://github.com/swarnavarsha1/adf_pipeline_monitor_ai_agent.git
    cd adf_pipeline_monitor_ai_agent
    ```

2. **Create and activate a Python virtual environment:**

    ```
    python -m venv venv

    # Windows
    venv\Scripts\activate

    # macOS/Linux
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```

4. **Create a `.env` file** in the project root with your configuration:

    ```
    ADF_SUBSCRIPTION_ID=your-azure-subscription-id
    ADF_RESOURCE_GROUP=your-azure-resource-group
    ADF_FACTORY_NAME=your-adf-factory-name
    ADF_TENANT_ID=your-azure-tenant-id
    ADF_CLIENT_ID=your-service-principal-client-id
    ADF_CLIENT_SECRET=your-service-principal-client-secret
    OPENAI_API_KEY=your-openai-api-key
    NOTIFICATION_EMAIL=your-team-email@example.com

    # Optional SMTP settings (for real email notifications)
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=your_email@gmail.com
    SMTP_PASSWORD=your_app_password
    ```

5. **Run the monitoring system:**

    ```
    python main.py
    ```

    - The system polls your ADF pipelines every 2 minutes.
    - If failures occur, AI analyzes and decides rerun actions.
    - Notifications print to console or send emails (if SMTP configured).

6. **Stop the system anytime** by pressing `Ctrl+C`.

- Repeat polling loop after configured sleep time.

## Retrieval‑Augmented Generation (RAG) Integration

This monitoring agent now uses a RAG system to suggest fixes for pipeline failures from a PDF knowledge base.

How it works:

1. Put your reference PDFs (with error messages and solutions) into the knowledge_pdfs/ folder.

2. Build the search index (run from project root):

```
python -m rag.build_rag_index
```

This processes the PDFs into a FAISS vector store in rag/faiss_index/.

3. When a pipeline fails, the AI (GPT) diagnoses the cause and sends that to the RAG retriever.

4. The retriever finds similar solutions in your PDFs and includes them in the same notification with the AI rationale.

5. Duplicate notifications for the same run ID are suppressed — you only get one combined email per failure unless a new run fails.

## How It Works

- Monitor ADF pipelines at fixed intervals using the Azure Data Factory REST API.
- Detect failed and successful runs and update retry tracking in a local SQLite database.
- For each new failure, send details to GPT to decide retry action (full, partial, or none) and explain why.
- If retry advised → trigger rerun automatically via ADF API.
- Pass GPT’s rationale to the RAG retriever to search your PDF knowledge base for matching solutions.
- Combine AI decision + RAG solution (and escalation note if retry is useless) into one notification.
- Send the notification to configured recipients (currently printed, email integration possible).
- Avoid duplicate notifications for the same run ID using DB flags, only re‑alert if a new failure/run occurs.


``` mermaid
flowchart TD
    A[Monitor Pipelines via ADF API]:::step --> B[Failure Detected<br>pipeline_name, run_id, error_message]:::step
    B --> C[AI Analysis - GPT<br/>-  Suggest retry: full / partial / none<br/>-  Provide rationale]:::ai
    C --> D[RAG Solution Lookup<br/>-  Use AI rationale as search query<br/>-  Search FAISS vector store from PDFs<br/>-  Find matching KB chunks<br/>-  Ask GPT to summarize solution]:::rag
    D --> E[Single Combined Notification<br/>-  Pipeline name & run ID<br/>-  AI decision & rationale<br/>-  Suggested KB solution<br/>-  Escalation note if retry won't help]:::notif

    classDef step fill:#CDE8FF,stroke:#0366d6,stroke-width:2px,color:#000,font-weight:bold
    classDef ai fill:#FFD6D6,stroke:#d73a49,stroke-width:2px,color:#000,font-weight:bold
    classDef rag fill:#FFF3CD,stroke:#e36209,stroke-width:2px,color:#000,font-weight:bold
    classDef notif fill:#D4F8D4,stroke:#28a745,stroke-width:2px,color:#000,font-weight:bold
```