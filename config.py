# Store configuration (populate with your secrets in development only—use KeyVault/env vars in prod!)
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

ADF_SUBSCRIPTION_ID = os.getenv('ADF_SUBSCRIPTION_ID')
ADF_RESOURCE_GROUP = os.getenv('ADF_RESOURCE_GROUP')
ADF_FACTORY_NAME = os.getenv('ADF_FACTORY_NAME')
ADF_TENANT_ID = os.getenv('ADF_TENANT_ID')
ADF_CLIENT_ID = os.getenv('ADF_CLIENT_ID')
ADF_CLIENT_SECRET = os.getenv('ADF_CLIENT_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')

