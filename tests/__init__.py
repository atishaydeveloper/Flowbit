import pytest
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.test'))

# Test environment setup with default values
test_env = {
    'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY', 'test_api_key'),
    'MODEL_NAME': os.getenv('MODEL_NAME', 'gemini-pro'),
    'TEST_MODE': os.getenv('TEST_MODE', 'True'),
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'DEBUG'),
    'TEST_DATA_DIR': os.getenv('TEST_DATA_DIR', 'tests/data'),
    'TEST_DB_PATH': os.getenv('TEST_DB_PATH', ':memory:'),
    'JSON_SCHEMA_PATH': os.getenv('JSON_SCHEMA_PATH', 'data/json_schema.json'),
    'EMAIL_SCHEMA_PATH': os.getenv('EMAIL_SCHEMA_PATH', 'data/email_schema.json')
}

# Apply test environment variables, ensuring all values are strings
for key, value in test_env.items():
    if value is not None:
        os.environ[key] = str(value)
    else:
        raise ValueError(f"Environment variable {key} is not set and has no default value")