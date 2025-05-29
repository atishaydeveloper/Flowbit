import pytest
from main import process_email_input

@pytest.mark.asyncio
async def test_process_email_input(sample_email_text):
    result = await process_email_input(sample_email_text, "RFQ")
    assert "extracted_sender_name" in result
    assert "primary_request_summary" in result
    assert "urgency_level" in result

@pytest.mark.asyncio
async def test_empty_email():
    with pytest.raises(ValueError):
        await process_email_input("", "RFQ")