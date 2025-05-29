import pytest
from utils.email_utils import strip_html, extract_email_parts

def test_strip_html_basic():
    """Test basic HTML stripping."""
    html_content = """
    <html>
    <body>
        <p>Hello,</p>
        <div>This is a test email</div>
        <br>
        <p>Best regards,<br>John</p>
    </body>
    </html>
    """
    expected = "Hello,\n\nThis is a test email\n\nBest regards,\nJohn"
    result = strip_html(html_content)
    assert result.strip() == expected.strip()

def test_strip_html_with_no_html():
    """Test stripping when no HTML is present."""
    plain_text = "Hello,\nThis is plain text.\nRegards"
    result = strip_html(plain_text)
    assert result == plain_text

def test_extract_email_parts():
    """Test email parts extraction."""
    email_content = """
    Subject: Test Email
    From: sender@example.com
    To: recipient@example.com

    Hello,
    This is the body.
    Regards
    """
    parts = extract_email_parts(email_content)
    assert parts["subject"] == "Test Email"
    assert parts["from"] == "sender@example.com"
    assert parts["to"] == "recipient@example.com"
    assert "Hello," in parts["body"]