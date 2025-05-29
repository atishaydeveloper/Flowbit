import pytest
import json
from main import process_json_input

@pytest.mark.asyncio
async def test_process_json_input(sample_json_data):
    """Test successful JSON processing."""
    json_str = json.dumps(sample_json_data)
    result = await process_json_input(json_str, "Invoice")
    
    # Verify response structure
    assert isinstance(result, dict)
    assert "flowbit_formatted_data" in result
    assert "processing_report" in result
    
    # Verify processing report
    assert result["processing_report"]["status"] == "success"
    assert not result["processing_report"]["missing_required_fields"]
    
    # Verify formatted data
    formatted_data = result["flowbit_formatted_data"]
    assert formatted_data["invoiceId"] == sample_json_data["invoice_id"]
    assert formatted_data["customerName"] == sample_json_data["customer"]["name"]

@pytest.mark.asyncio
async def test_process_json_with_missing_fields(sample_json_data):
    """Test JSON processing with missing required fields."""
    del sample_json_data["invoice_id"]
    json_str = json.dumps(sample_json_data)
    result = await process_json_input(json_str, "Invoice")
    
    # Verify missing field detection
    assert result["processing_report"]["status"] == "error"
    assert "invoiceId" in result["processing_report"]["missing_required_fields"]  # Changed from 'invoice_id' to 'invoiceId'
    assert "flowbit_formatted_data" in result  # Should still have partial data