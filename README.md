# Email Parsing Agent

A Python agent that uses **Ollama (llama3.2)** and **LangChain** to intelligently parse emails and extract structured information.

## What This Does

Takes raw email text and automatically extracts:
- **Sender**: Who sent the email
- **Subject**: Email subject line
- **Date**: When it was sent
- **Main Intent**: What the email is primarily about (1-2 sentences)
- **Action Items**: Specific tasks or requests mentioned
- **Urgency Level**: classified as high/medium/low

Returns structured JSON output that's ready for downstream processing.

## Architecture Overview

```
Raw Email Text
     ↓
[LangChain PromptTemplate] - Formats email into a structured prompt
     ↓
[OllamaLLM] - Calls local llama3.2 model running in Ollama
     ↓
JSON Response - Model outputs structured data
     ↓
[Pydantic Validation] - Validates data types and structure
     ↓
EmailData Object - Type-safe Python object
```

### Key Components

**OllamaLLM**: Connects to your local Ollama instance (running on localhost:11434 by default). This keeps all processing local and private—no API keys needed.

**PromptTemplate**: Guides the LLM with clear instructions on what to extract from each email. The prompt is carefully crafted to request JSON output for reliable parsing.

**LLMChain**: Orchestrates the flow—it takes your email, formats it with the prompt template, sends it to Ollama, and returns the result.

**Pydantic EmailData Model**: Validates the extracted data. If the LLM returns invalid data (wrong types, missing fields), Pydantic raises a clear error.

## Setup Instructions

### 1. Ensure Ollama is Running

Make sure you have Ollama installed and running locally:

```bash
ollama serve  # In one terminal
ollama pull llama3.2  # Download the model (run once)
```

Ollama should be accessible at `http://localhost:11434`

### 2. Clone and Setup Project

```bash
cd email-agent
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
cp .env.example .env
# Edit .env if you need non-default settings
```

## Usage

### Option 1: Using the Convenience Function

```python
from src.email_parser import parse_email

email_text = """
From: boss@company.com
To: you@company.com
Subject: Q2 Report Due

Please complete the Q2 budget report by EOD today.

Thanks
"""

result = parse_email(email_text)
print(result.sender)           # 'boss@company.com'
print(result.urgency_level)    # 'high'
print(result.action_items)     # ['complete the Q2 budget report by EOD']
```

### Option 2: Using the Agent Class Directly

```python
from src.email_parser import EmailParserAgent

agent = EmailParserAgent(
    model_name="llama3.2",
    ollama_base_url="http://localhost:11434"
)

result = agent.parse_email(email_text)

# Access as attributes
print(result.sender)
print(result.subject)
print(result.main_intent)
print(result.urgency_level)
print(result.action_items)

# Or as a dictionary
print(result.model_dump())  # Pydantic method to get dict
print(result.model_dump_json())  # Get JSON string
```

## Running Tests

The project includes comprehensive test cases with sample emails demonstrating different scenarios:

```bash
python tests/test_parser.py
```

Or with pytest:
```bash
python -m pytest tests/test_parser.py -v
```

Tests cover:
- **Urgent emails** with explicit action items and high urgency
- **Informational emails** with low urgency and no action items
- **Meeting requests** with multiple options and medium urgency

## How It Works: Step-by-Step

### When You Call `parse_email()`:

1. **Prompt Formatting** - Email text is inserted into the prompt template
   - The template includes instructions for JSON format
   - Guides the model on what fields to extract

2. **LLM Inference** - Ollama runs llama3.2 with the formatted prompt
   - Low temperature (0.3) for consistent, factual outputs
   - Num_predict=500 limits output length for speed

3. **Response Parsing** - The returned text is cleaned
   - Removes markdown code blocks if present
   - Extracts raw JSON

4. **Validation** - Pydantic validates the JSON
   - Ensures sender, subject, main_intent are strings
   - Ensures action_items is a list
   - Ensures urgency_level is one of: high/medium/low
   - Raises clear errors if data is invalid

5. **Return** - You get a typed EmailData object

### Prompt Engineering

The prompt in `src/prompts.py` is carefully designed to:
- Request structured JSON output
- Specify each field clearly
- Provide example output format
- Guide urgency classification

This reduces hallucination and improves consistency.

## Customization

### Change the Model

```python
agent = EmailParserAgent(
    model_name="llama2",  # Use a different Ollama model
    ollama_base_url="http://localhost:11434"
)
```

Available Ollama models: run `ollama list` to see what you have installed

### Adjust Model Behavior

Edit the `EmailParserAgent.__init__()` method:
```python
self.llm = OllamaLLM(
    model=model_name,
    base_url=ollama_base_url,
    temperature=0.1,  # Lower = more consistent, Higher = more creative
    num_predict=300,  # Max tokens to generate
)
```

### Modify Extracted Fields

To extract different information, edit `src/prompts.py` and the `EmailData` class in `src/email_parser.py`.

## Limitations & Notes

- **Offline Only**: Requires Ollama running locally. No cloud API calls.
- **Model Size**: llama3.2 is 3.2B parameters. Smaller than GPT-4 but runs locally on modest hardware.
- **Token Limit**: Context window limits email size. Very long emails (10K+ tokens) may be truncated.
- **Accuracy**: Local LLMs are less accurate than GPT-4. Test with your specific emails.
- **Speed**: First inference is slower (model loads). Subsequent calls are faster.

## Requirements

- Python 3.9+
- Ollama (https://ollama.ai)
- llama3.2 model (download via `ollama pull llama3.2`)
- Dependencies: langchain, langchain-ollama, pydantic, python-dotenv

## Project Structure

```
email-agent/
├── src/
│   ├── __init__.py
│   ├── email_parser.py      # Main EmailParserAgent class
│   └── prompts.py           # Prompt templates
├── tests/
│   ├── __init__.py
│   └── test_parser.py       # Test cases with sample emails
├── venv/                    # Virtual environment
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Troubleshooting

### Connection Error: "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check URL is correct: `http://localhost:11434`
- Try: `curl http://localhost:11434/api/tags` to test connection

### "Model not found" Error
- Download the model: `ollama pull llama3.2`
- List available models: `ollama list`

### JSON Parse Error
- The LLM sometimes returns invalid JSON
- Try lowering temperature further for more consistent output
- Check the raw response in the error message

### Slow Inference
- First call loads the model (~1-2 minutes on first run)
- Subsequent calls are much faster
- Smaller models (e.g., llama2) are faster but less accurate

## Next Steps

Consider extending this agent to:
- **Priority Inbox**: Automatically sort by urgency
- **Calendar Integration**: Parse meeting requests and create events
- **Task Manager Integration**: Push action items to your task manager
- **Email Classification**: Automatically tag emails by type
- **Batch Processing**: Process folders of emails
- **Web API**: Wrap the agent in a FastAPI server

---

Built with ❤️ using LangChain, Ollama, and Python
