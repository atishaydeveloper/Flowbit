# imports
from chains import classifier_agent_chain, JSON_agent_chain, email_parser_agent_chain, clean_json_response, decide_next_agent, intent_type, get_schema_for_intent
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.retry import retry_with_exponential_backoff, RetryError
from langchain_core.exceptions import OutputParserException
from utils.email_utils import strip_html, extract_email_parts
from dotenv import load_dotenv
import json
import logging
from typing import Dict, Any
import fitz 
import asyncio
import uuid
from memory import SharedMemory
from datetime import datetime
import os 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# llm initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    convert_system_message_to_human=True  # Add this parameter
)

# Custom error for processing failures
class ProcessingError(Exception):
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


@retry_with_exponential_backoff(
    max_retries=3,
    exceptions=(OutputParserException, ConnectionError, ValueError)
)

# pdf validation
async def is_valid_pdf(pdf_path: str) -> bool:
    try:
        doc = fitz.open(pdf_path)
        doc.close()
        return True
    except Exception:
        return False

# text extraction from pdfs, json and txt files
async def is_file_input(file_path: str) -> bool:
    """Check if the input is a file path."""
    return any(file_path.lower().endswith(ext) for ext in ['.pdf', '.json', '.txt'])

async def read_file_content(file_path: str) -> str:
    """Read content from different file types."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle PDF files
        if file_path.lower().endswith('.pdf'):
            if not await is_valid_pdf(file_path):
                raise ValueError("Invalid PDF file")
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
            
        # Handle JSON files
        elif file_path.lower().endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        # Handle TXT files
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
            
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise

async def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF with error handling and validation"""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not is_valid_pdf(pdf_path):
            raise ValueError("Invalid PDF file")
            
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise
    
# getting user input
async def get_user_input() -> str:
    """Get multi-line input from user or read from file."""
    print("Enter your text (end with ':q' on a new line or Ctrl+Z+Enter):")
    print("Or enter a file path (.pdf, .json, or .txt)")
    lines = []
    
    try:
        while True:
            line = input()
            if await is_file_input(line):
                return await read_file_content(line)
            elif line.strip() == ':q':
                break
            lines.append(line)
    except EOFError:
        pass
    
    return '\n'.join(lines)

# using classifier agent on the user input
async def classify_input(input_data: str) -> Dict[str, Any]:
    """Classify input using the classifier agent with retry logic."""
    if not input_data:
        raise ValueError("Empty input data")
        
    try:
        response = classifier_agent_chain.invoke({
            "input_text": input_data,
            "messages": [{
                "role": "user",
                "content": input_data
            }]
        })
        
        if not hasattr(response, 'content'):
            raise ProcessingError("Invalid response from classifier agent")
            
        return clean_json_response(response.content)
        
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise ProcessingError("Failed to classify input", {
            "error": str(e),
            "input_length": len(input_data)
        })

# initializing json agent
async def process_json_input(input_data: str, intent: str) -> Dict[str, Any]:
    """Process input using JSON agent with schema."""
    schema = get_schema_for_intent(intent)
    response = JSON_agent_chain.invoke({
        "input_json": input_data, 
        "schema": json.dumps(schema, indent=2),
        "messages": [{
            "role": "user",
            "content": input_data
        }]
    })
    return clean_json_response(response.content)

# initializing email agent
async def process_email_input(input_data: str, intent: str) -> Dict[str, Any]:
    """Process input using email parser agent."""
    if not input_data.strip():
        raise ValueError("Empty email content")

    # Clean HTML and extract parts
    cleaned_content = strip_html(input_data)
    email_parts = extract_email_parts(cleaned_content)
    
    response = email_parser_agent_chain.invoke({
        "email_text": cleaned_content,
        "email_parts": email_parts,
        "intent": intent,
        "messages": [{
            "role": "user",
            "content": cleaned_content
        }]
    })
    return clean_json_response(response.content)

# Process input with enhanced error handling and retry logic
async def process_input(input_data: str, input_type: str = None) -> Dict[str, Any]:
    memory = SharedMemory()
    input_id = str(uuid.uuid4())
    
    try:
        # Input validation
        if not input_data:
            raise ValueError("Empty input data")
            
        # Store input
        memory.store_input(input_id, input_data, input_type)
        
        try:
            # Process with classifier
            classification = await classify_input(input_data)
            memory.store_classification(input_id, classification)
            
            # Route to appropriate agent
            agent_type = decide_next_agent(classification)
            intent = intent_type(classification)
            
            # Process with selected agent
            if agent_type == "JSON_agent":
                result = await process_json_input(input_data, intent)
            else:
                result = await process_email_input(input_data, intent)
                
            memory.store_result(input_id, result)
            
            return {
                "input_id": input_id,
                "classification": classification,
                "result": result,
                "status": "success"
            }
            
        except RetryError as e:
            logger.error(f"Retry attempts exhausted: {str(e)}")
            raise ProcessingError("Processing failed after multiple retries", {
                "retry_error": str(e)
            })
            
        except ProcessingError as e:
            logger.error(f"Processing error: {str(e)}", extra=e.details)
            raise
            
    except Exception as e:
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
        logger.error("Processing failed", extra=error_details)
        
        return {
            "input_id": input_id,
            "error": str(e),
            "error_details": error_details,
            "status": "error"
        }

async def main_async():
    """Async main program loop."""
    load_dotenv()
    
    print("FlowBit Document Processor")
    print("-------------------------")
    print("Input Options:")
    print("- Type your text (multiple lines allowed)")
    print("- End input with ':q' on a new line")
    print("- Or use Ctrl+Z+Enter")
    print("- Type 'exit' to quit the program")
    print("-------------------------")
    
    while True:
        user_text = await get_user_input()  # Added await here
        if user_text.lower() == 'exit':
            print("Goodbye!")
            break
        elif not user_text.strip():
            continue
            
        result = await process_input(user_text)
        print("\nProcessing Result:")
        print(json.dumps(result, indent=2))
        print("-------------------------")

if __name__ == "__main__":
    asyncio.run(main_async())

