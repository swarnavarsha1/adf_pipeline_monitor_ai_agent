# ADF AI Pipeline Monitor

This project implements a smart **AI-powered monitoring system for Azure Data Factory (ADF) pipelines** using OpenAI’s GPT-4. It helps you:

- Automatically detect when ADF pipelines fail.
- Send failure details to GPT-4 for intelligent analysis.
- Let GPT-4 decide whether to rerun the full pipeline, rerun just the failed part, or skip rerun.
- Automatically trigger pipeline reruns based on AI decisions.
- Notify your team via email or console alerts about failures and actions taken.

This makes your data pipelines more resilient and reduces manual troubleshooting.

---

## Features

- Continuous, near-real-time failure monitoring of ADF pipelines.
- AI-driven decision making with GPT-4 for intelligent recovery.
- Automated pipeline reruns (full or partial).
- Notification support via email
- Modular architecture for easy customization.

---

## Prerequisites

- Azure subscription with Azure Data Factory pipelines.
- Azure Service Principal with rights to read/run pipelines.
- Access to Azure OpenAI service with GPT-4 enabled.
- Python 3.8 or newer.
- (Optional) SMTP email account credentials for notifications.

---

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

---

## How It Works

- **Monitoring Agent** checks pipeline runs regularly.
- **Decision Logic Agent** sends failure info to GPT-4.
- GPT-4 suggests rerun full, partial, or no rerun.
- **Trigger Rerun Agent** calls Azure APIs to rerun pipelines automatically.
- **Notifier Agent** alerts operations by printing or email.

---

