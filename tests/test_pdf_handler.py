import pytest
import os
from main import is_pdf, is_valid_pdf, extract_text_from_pdf

@pytest.mark.asyncio
async def test_is_pdf():
    assert await is_pdf("document.pdf") == True
    assert await is_pdf("document.txt") == False

@pytest.mark.asyncio
async def test_is_valid_pdf(sample_pdf_path):
    assert await is_valid_pdf(sample_pdf_path) == True
    assert await is_valid_pdf("nonexistent.pdf") == False

@pytest.mark.asyncio
async def test_extract_text_from_pdf(sample_pdf_path):
    text = await extract_text_from_pdf(sample_pdf_path)
    assert isinstance(text, str)
    assert len(text) > 0

@pytest.mark.asyncio
async def test_extract_text_from_nonexistent_pdf():
    with pytest.raises(FileNotFoundError):
        await extract_text_from_pdf("nonexistent.pdf")