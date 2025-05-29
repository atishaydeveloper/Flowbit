# imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import re
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# load environment variables
load_dotenv()

# llm initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    convert_system_message_to_human=True  # Add this parameter
)

# response processing
def clean_json_response(response_text):
    """Clean and parse JSON response from LLM."""
    # Remove ```json at the start and ``` at the end
    cleaned = re.sub(r'^```json\s*|\s*```$', '', response_text.strip())
    try:
        response_dict = json.loads(cleaned)
        return response_dict
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        return {
            "error": "Failed to parse JSON response",
            "raw_response": response_text
        }

# utilizing suitable agent as per the input format
def decide_next_agent(response):
    if response["classified_format"] == "Email_Text":
        return "Email_agent"
    elif response["classified_format"] == "JSON":
        return "JSON_agent"
    else:
        return "Email_agent"
    
# extracting the intent of the user input
def intent_type(response):
    if response["classified_intent"] == "RFQ":
        return "RFQ"
    elif response["classified_intent"] == "Invoice":
        return "Invoice"
    elif response["classified_intent"] == "Complaint":
        return "Complaint"
    elif response["classified_intent"] == "Regulation":
        return "Regulation"
    elif response["classified_intent"] == "General_Inquiry":
        return "General_Inquiry"
    elif response["classified_intent"] == "Order_Confirmation":
        return "Order_Confirmation"
    elif response["classified_intent"] == "Support_Request":
        return "Support_Request"
    else:
        return "Other"
    
# mapping suitable schema for the intent from json_schema.json file
def get_schema_for_intent(intent_type):
    """Get schema for given intent type with proper path handling."""
    schema_path = os.path.join(os.path.dirname(__file__), "data", "json_schema.json")
    
    if not os.path.exists(schema_path):
        
        schema_path = os.path.join(os.path.dirname(__file__), "tests", "data", "json_schema.json")
    
    with open(schema_path, 'r') as f:
        schemas = json.load(f)
    
    intent_to_schema = {
        "Invoice": "FlowBitInvoiceV1",
        "RFQ": "FlowBitRFQ_V1",
        "Complaint": "FlowBitComplaint_V1", 
        "Regulation": "FlowBitRegulation_V1",
        "General_Inquiry": "FlowBitGeneralInquiry_V1",
        "Order_Confirmation": "FlowBitOrderConfirmation_V1",
        "Support_Request": "FlowBitSupportRequest_V1",
        "Other": "FlowBitGenericData_V1"
    }
    
    schema_name = intent_to_schema.get(intent_type, "FlowBitGenericData_V1")
    return next((schema for schema in schemas if schema["schema_name"] == schema_name), schemas[-1])

# defining classifier agent
classifier_agent_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        """You are an AI Classification Specialist. Your task is to analyze the provided input data to determine its format and primary intent.

        **Context:**
        The input data you receive could be text extracted from a PDF document, a JSON payload, or the body text of an email. Your goal is to accurately classify both the format of the original input (based on the provided text) and the underlying purpose or intent of the message.

        **Available Intents:**
        You must classify the intent into one of the following categories:
        * `Invoice`: Documents detailing a transaction, listing products/services, costs, and payment dues.
        * `RFQ` (Request for Quotation): Inquiries seeking pricing, proposals, or bids for specific goods or services.
        * `Complaint`: Expressions of dissatisfaction, issues, or grievances regarding a product, service, or experience.
        * `Regulation`: Official rules, guidelines, legal notices, compliance documents, or government mandates.
        * `General_Inquiry`: General questions, requests for information not fitting other specific categories.
        * `Order_Confirmation`: Confirmation of a placed order, detailing items and expected delivery/fulfillment.
        * `Support_Request`: A request for help, technical assistance, or customer service.
        * `Other`: If the intent is ambiguous or does not clearly fit into any of the above categories.

        **Input Data:** {input_text}

        **Instructions:**

        1. **Format Analysis:** Classify the format as one of:
           * `JSON`: If structured with key-value pairs, nested objects, or arrays
           * `Email_Text`: If contains email elements like salutations
           * `PDF_Content`: If appears to be from a formal document
           * `Undetermined_Format`: If unclear

        2. **Intent Analysis:** Determine the most appropriate intent from the available categories.

        3. **Output Format:**
        {{
            "classified_format": "<format>",
            "classified_intent": "<intent>",
            "reasoning": "<explanation>"
        }}

        Return your classification in the exact JSON format shown above.
        """
    ),
    MessagesPlaceholder(variable_name="messages"),
])

classifier_agent_chain = classifier_agent_prompt | llm

# defining Json agent
JSON_agent_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        """You are an AI JSON Processing Agent. Process the input according to the schema.

        Input JSON: {input_json}
        Schema Definition: {schema}

        Process the input using the schema and return:
        {{
            "flowbit_formatted_data": {{
                // Processed data according to schema
            }},
            "processing_report": {{
                "schema_used": "schema_name",
                "status": "success/error",
                "missing_required_fields": [],
                "type_mismatches": [],
                "unmapped_source_fields": []
            }}
        }}
        """
    ),
    MessagesPlaceholder(variable_name="messages"),
])

JSON_agent_chain = JSON_agent_prompt | llm

# defining email parser agent
Email_parser_agent_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        """You are an AI Email Processing Specialist. Extract information from the email.

        Email Text: {email_text}
        Intent Classification: {intent}

        Extract and return:
        {{
            "extracted_sender_name": "name",
            "primary_request_summary": "summary",
            "key_entities_mentioned": [],
            "urgency_level": "Low/Medium/High/Specific_Date_Requested",
            "urgency_reason_or_deadline": "reason",
            "sentiment": "Positive/Neutral/Negative",
            "action_items_implied": [],
            "contact_information_in_body": []
        }}
        """
    ),
    MessagesPlaceholder(variable_name="messages"),
])


email_parser_agent_chain = Email_parser_agent_prompt | llm

