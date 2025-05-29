import pytest
from main import classify_input, ProcessingError

@pytest.mark.asyncio
async def test_classify_email(sample_email_text):
    result = await classify_input(sample_email_text)
    assert result["classified_format"] == "Email_Text"
    assert result["classified_intent"] == "RFQ"
    assert "reasoning" in result

@pytest.mark.asyncio
async def test_classify_json(sample_json_data):
    result = await classify_input(str(sample_json_data))
    assert result["classified_format"] == "JSON"
    assert result["classified_intent"] == "Invoice"
    assert "reasoning" in result

@pytest.mark.asyncio
async def test_empty_input():
    with pytest.raises(ValueError, match="Empty input data"):
        await classify_input("")