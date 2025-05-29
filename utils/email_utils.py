from bs4 import BeautifulSoup
import re
from typing import Dict, Any

def strip_html(content: str) -> str:
    """
    Strip HTML from email content while preserving structure.
    
    Args:
        content: Email content that may contain HTML
        
    Returns:
        Clean text with preserved line breaks and spacing
    """
    if not content:
        return ""
        
    # Check if content appears to be HTML
    if '<' in content and '>' in content:
        try:
            # Parse HTML and extract text
            soup = BeautifulSoup(content, 'html.parser')
            
            # Handle br tags first
            for br in soup.find_all('br'):
                br.replace_with('\n')
            
            # Handle paragraphs and divs
            for tag in soup.find_all(['p', 'div']):
                tag.insert_before(soup.new_string('\n'))
                tag.append(soup.new_string('\n'))
            
            # Get text and clean up whitespace
            text = soup.get_text()
            # Normalize line endings
            text = re.sub(r'\r\n?', '\n', text)
            # Remove multiple newlines
            text = re.sub(r'\n\s*\n', '\n\n', text)
            return text.strip()
            
        except Exception as e:
            return _basic_html_cleanup(content)
    
    return content

def _basic_html_cleanup(content: str) -> str:
    """Basic HTML cleanup using regex for fallback."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', content)
    # Fix spacing
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_email_parts(content: str) -> Dict[str, Any]:
    """
    Extract key parts from email content.
    
    Args:
        content: Raw email content with headers and body
        
    Returns:
        Dict containing subject, from, to, and body
    """
    parts = {
        'subject': '',
        'from': '',
        'to': '',
        'body': ''
    }
    
    # Normalize line endings and split into lines
    content = content.replace('\r\n', '\n')
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    body_start = 0
    
    # Find headers
    for i, line in enumerate(lines):
        # Find first empty line indicating start of body
        if not line:
            body_start = i + 1
            continue
            
        # Extract headers
        lower_line = line.lower()
        if lower_line.startswith('subject:'):
            parts['subject'] = line[8:].strip()
        elif lower_line.startswith('from:'):
            parts['from'] = line[5:].strip()
        elif lower_line.startswith('to:'):
            parts['to'] = line[3:].strip()
        
        # If we find a non-header line, assume it's the body start
        if not any(lower_line.startswith(h) for h in ['subject:', 'from:', 'to:']):
            body_start = i
            break
    
    # Get body (everything after headers)
    if body_start < len(lines):
        parts['body'] = '\n'.join(lines[body_start:]).strip()
    
    return parts