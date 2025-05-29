import pytest
import os
from typing import Dict, Any

@pytest.fixture
def sample_pdf_path() -> str:
    return os.path.join(os.path.dirname(__file__), "data", "sample.pdf")

@pytest.fixture
def test_env():
    """Fixture to access test environment variables"""
    return {key: os.getenv(key) for key in [
        'GOOGLE_API_KEY',
        'MODEL_NAME',
        'TEST_MODE',
        'LOG_LEVEL',
        'TEST_DATA_DIR',
        'TEST_DB_PATH',
        'JSON_SCHEMA_PATH',
        'EMAIL_SCHEMA_PATH'
    ]}
  
@pytest.fixture    
def sample_email_text() -> str:
    return """
    Subject: Request for Quotation
    From: john.doe@example.com
    
    Dear Sales Team,
    
    I would like to request a quotation for:
    - 100 units of Product A
    - 200 units of Product B
    
    Delivery needed by end of next month.
    
    Best regards,
    John Doe
    """
@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    class MockLLM:
        async def invoke(self, *args, **kwargs):
            return {
                "content": """
                {
                    "classified_format": "Email_Text",
                    "classified_intent": "RFQ",
                    "reasoning": "Test reasoning"
                }
                """
            }
    return MockLLM()

@pytest.fixture
def mock_shared_memory():
    """Mock SharedMemory for testing"""
    class MockSharedMemory:
        def store_input(self, *args, **kwargs):
            pass
        def store_classification(self, *args, **kwargs):
            pass
        def store_result(self, *args, **kwargs):
            pass
    return MockSharedMemory()


@pytest.fixture
def sample_json_data() -> Dict[str, Any]:
    return {
        "invoice_id": "INV-2023-001",
        "customer": {
            "name": "Acme Corp",
            "email": "billing@acme.com"
        },
        "items": [
            {"product": "Widget A", "quantity": 5, "price": 100},
            {"product": "Widget B", "quantity": 2, "price": 200}
        ]
    }