## FlowBit
Intelligent document processing with multi-agent AI for classifying, extracting, and formatting data from emails, JSON, PDFs, and more.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Key Capabilities](#key-capabilities)
3. [Features](#features)
4. [Directory Structure](#directory-structure)
5. [Getting Started](#getting-started)
6. [Usage](#usage)
7. [API Reference](#api-reference)
8. [Testing](#testing)
9. [Error Handling](#error-handling)
10. [Contributing](#contributing)
11. [Future Enhancements](#future-enhancements)
12. [License](#license)

---

## 🖥️ Project Overview

FlowBit is an **intelligent document processing** system leveraging multiple AI agents to automatically process, classify, and extract information from diverse inputs. It combines schema validation, multi-agent classification, and robust storage to deliver structured, audit-ready outputs.

---

## 🚀 Key Capabilities

### 1. Multi-Format Input Processing

* **PDF Documents**

  * Extracts text content
  * Handles multi-page documents
  * Validates PDF structure
  * Preserves document formatting
* **JSON Data**

  * Processes structured data
  * Validates against predefined schemas
  * Handles nested objects and arrays
  * Supports type coercion
* **Email Content**

  * Processes plain text and HTML emails
  * Strips HTML formatting
  * Extracts headers and metadata
  * Preserves email structure

### 2. Intelligent Classification

* Auto-detects input format (PDF, JSON, Email)
* Determines document intent/type:

  * Invoices, RFQs, Complaints, Support Requests
  * General Inquiries, Order Confirmations, Regulations

### 3. Smart Data Extraction

* **JSON Documents**

  * Field mapping, data transformation
  * Schema validation, anomaly detection
* **Emails**

  * Sender info, request summaries
  * Urgency levels, action items
  * Contact info, sentiment analysis

### 4. Persistent Storage

* Stores all processed documents
* Maintains full processing history
* Links related records for context
* Enables comprehensive audit trails

### 5. Use Cases

1. Business Document Automation
2. Customer Communication Analysis
3. Data Integration Pipelines

---

## ⚙️ Features

* **Multi-agent architecture** for classification, parsing, and formatting
* **Schema-driven** validation using JSON schema files
* **Persistent memory** via SQLite for audit and debugging
* **Retry mechanisms** for reliable AI calls
* **Comprehensive test suite** covering unit and end-to-end scenarios

---

## 📂 Directory Structure

```plaintext
flowbit/
├── data/
│   ├── json_schema.json        # JSON-schema definitions
│   └── email_schema.json       # Email field mapping schemas
├── utils/
│   ├── email_utils.py          # HTML stripping, parsing helpers
│   └── retry.py                # Exponential backoff utility
├── tests/
│   ├── data/                   # Sample inputs (PDF, email, JSON)
│   ├── test_html_stripping.py
│   ├── test_json_processor.py
│   └── test_pdf_handler.py
├── chains.py                   # LLM chains and prompts
├── memory.py                   # SQLite-based persistence layer
├── main.py                     # Entry-point orchestrator
├── requirements.txt            # Python dependencies
└── pytest.ini                  # Pytest configuration
```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* `pip` package manager

### Installation

```bash
# Clone the repo
git clone https://github.com/your-org/flowbit.git
cd flowbit
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate    # (Linux/macOS)
.\.venv\Scripts\activate # (Windows)
# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory with:

```env
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-2.0-flash
```

---

## 💡 Usage

Run the CLI to process documents:

```bash
python main.py
```

View database contents:
```bash
python view_db.py view-inputs
python view_db.py view-classifications
python view_db.py view-results
```

* **Input Modes**:

  * Paste text (end with `:q` on a new line)
  * Type `exit` to quit

---

## 🛠️ API Reference

### `process_input`

```python
async def process_input(
    input_data: str,
    input_type: Optional[str] = None
) -> Dict[str, Any]
```

**Returns**:

```json
{
  "input_id": "uuid",
  "classification": {
    "classified_format": "email|json|pdf",
    "classified_intent": "invoice|report|etc."
  },
  "result": {
    "formatted_data": {...},
    "processing_report": {...}
  },
  "status": "success|error"
}
```

---

## 🧪 Testing

Run the full test suite:

```bash
pytest -v --cov=.
```

Run a specific test:

```bash
pytest -q tests/test_html_stripping.py
```

---

## ⚠️ Error Handling & Technical Features

* **Retry mechanisms** for API/AI calls
* **Detailed error reporting** and exception tracking
* **Data validation** and secure input sanitization
* **Async, scalable architecture** for high throughput
* **Modular design** with extensible components
* **Secure storage** with access tracking

---

## 🤝 Contributing

1. Fork the repo and create a feature branch (`git checkout -b feature/foo`)
2. Follow PEP 8 for code style
3. Add tests for new functionality
4. Submit a pull request with a clear description

---

## 🔮 Future Enhancements

* Support for additional document formats
* Enhanced ML models for smarter extraction
* Advanced analytics and reporting
* Real-time processing and custom schema support
* Web UI dashboard for monitoring and control

---


