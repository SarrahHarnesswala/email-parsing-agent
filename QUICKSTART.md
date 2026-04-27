# Quick Start Guide

Get the email parsing agent up and running in 5 minutes.

## Step 1: Verify Ollama is Running

In your terminal:

```bash
ollama serve
```

In another terminal, download the model:

```bash
ollama pull llama3.2
```

Verify it's working:

```bash
curl http://localhost:11434/api/tags
```

## Step 2: Activate Virtual Environment

```bash
cd email-agent
source venv/Scripts/activate  # On Windows (bash)
# or
venv\Scripts\activate.bat     # On Windows (cmd)
# or
source venv/bin/activate      # On macOS/Linux
```

You should see `(venv)` in your terminal prompt.

## Step 3: Test the Installation

Run the test suite:

```bash
python tests/test_parser.py
```

Expected output:
```
TEST 1: Urgent Email with Action Items
...
✓ Test passed!
```

## Step 4: Try the Demo

```bash
python demo.py
```

Follow the prompts to see the agent in action.

## Step 5: Parse Your Own Email

Create a new Python script:

```python
from src.email_parser import parse_email

email = """
From: someone@example.com
Subject: Hello

This is a test email.
"""

result = parse_email(email)
print(result.sender)           # someone@example.com
print(result.main_intent)      # Test email purpose
print(result.urgency_level)    # low
```

Run it:

```bash
python your_script.py
```

## What Each Component Does

### 1. **prompts.py** — The Instructions for Ollama

This file contains a carefully written prompt that tells llama3.2:
- What information to extract from emails
- What format to use (JSON)
- What each field means

**Why it matters**: A well-written prompt gets better results from the LLM. Vague prompts = inconsistent output.

### 2. **email_parser.py** — The Orchestrator

Three main classes/functions:

**EmailData (Pydantic Model)**:
```python
class EmailData(BaseModel):
    sender: str                      # Type validated
    subject: str                     # Type validated
    main_intent: str                 # Type validated
    action_items: list[str]          # Type validated
    urgency_level: str               # Type validated
```

Why Pydantic? If Ollama returns bad data, Pydantic catches it immediately with a clear error, instead of silently passing bad data downstream.

**EmailParserAgent (Main Class)**:
```python
agent = EmailParserAgent()
result = agent.parse_email(email_text)
```

What it does internally:
1. Creates an OllamaLLM instance (connects to localhost:11434)
2. Wraps the prompt template 
3. Creates an LLMChain (prompt → LLM → output)
4. Formats email into prompt
5. Calls Ollama
6. Parses JSON from response
7. Validates with Pydantic
8. Returns EmailData object

**parse_email() (Convenience Function)**:
```python
result = parse_email(email_text)
```

Shortcut for: `EmailParserAgent().parse_email(email_text)`

### 3. **test_parser.py** — Test Cases

Three realistic email examples:
- **Urgent request** - Boss wants a report ASAP
- **Informational** - Office hours announcement
- **Meeting request** - Client asking for availability

Why test? To verify the agent correctly extracts:
- Sender addresses
- Subjects
- Urgency levels
- Action items

## How the Extraction Works (Sequence)

```
You write:
┌─────────────────────────────────┐
│ Raw email text                  │
│ From: boss@company.com          │
│ Subject: Urgent Report Needed   │
│ ...                             │
└─────────────────────────────────┘
         ↓
Parse email with:
parse_email(email_text)
         ↓
┌─────────────────────────────────┐
│ PromptTemplate formats:         │
│ "Email: {raw_email}"            │
│ "Extract: sender, subject..."   │
│ "Return JSON: {...}"            │
└─────────────────────────────────┘
         ↓
OllamaLLM sends to llama3.2:
┌─────────────────────────────────┐
│ [Full formatted prompt]          │
│ Ollama at 11434 receives this   │
│ Runs llama3.2 locally           │
│ Returns JSON with extraction    │
└─────────────────────────────────┘
         ↓
JSON Parser extracts:
┌─────────────────────────────────┐
│ {"sender": "boss@company.com",  │
│  "subject": "Urgent...",        │
│  "urgency_level": "high",       │
│  ...}                           │
└─────────────────────────────────┘
         ↓
Pydantic validates types:
┌─────────────────────────────────┐
│ Confirms sender is string       │
│ Confirms action_items is list   │
│ Confirms urgency_level is valid │
└─────────────────────────────────┘
         ↓
Return EmailData object:
┌─────────────────────────────────┐
│ EmailData(                      │
│   sender="boss@company.com",    │
│   subject="Urgent Report...",   │
│   urgency_level="high",         │
│   action_items=[...],           │
│   ...                           │
│ )                               │
└─────────────────────────────────┘
```

## Key Concepts

### LangChain
A framework that chains together:
- LLM models (Ollama)
- Prompts (templates with variables)
- Data processing (parsing, validation)

Think of it as scaffolding around the LLM that handles the "glue."

### Ollama
Runs LLMs locally. No API calls, no keys, everything stays on your machine.

Model used: **llama3.2** (3.2B parameters, ~2GB disk)
- Small enough to run on modest hardware
- Large enough for many tasks
- Runs in ~1-2 seconds after first load

### Pydantic
Type validation library. Ensures your data matches the schema.

```python
# Valid - matches schema
EmailData(sender="someone@example.com", ...)

# Invalid - raises error immediately
EmailData(sender=123, ...)  # Email is not int!
EmailData(sender="test")    # Missing required fields!
```

### Prompt Engineering
The art of writing prompts that get the LLM to do what you want.

Our prompt does:
1. Sets context: "You are an email analysis expert"
2. Specifies task: "Extract these fields"
3. Shows format: "Return JSON like this: {...}"
4. Provides examples: Shows the structure

Better prompt → better results.

## Troubleshooting

### ❌ "Cannot connect to Ollama"
**Solution**: 
```bash
ollama serve  # Start Ollama in one terminal
```

### ❌ "llama3.2 model not found"
**Solution**:
```bash
ollama pull llama3.2  # Download it
ollama list           # Verify it exists
```

### ❌ "Invalid JSON" error
**Cause**: LLM returned malformed JSON

**Solution**: Lower temperature for more consistent output:
```python
agent = EmailParserAgent()
agent.llm.temperature = 0.1  # More consistent
```

### ❌ "Slow inference"
**Normal**: First call takes 1-2 minutes (model loads)

**Subsequent calls**: ~2-10 seconds depending on email length

**Optimization**: Use a smaller model (llama2) or GPU acceleration

## Next: Customization

Want to extract different fields? Check `README.md` for:
- Changing the prompt
- Using different models
- Adjusting LLM behavior
- Extending the EmailData model

## Need Help?

- Check `README.md` for full documentation
- Look at `tests/test_parser.py` for usage examples
- Look at `src/email_parser.py` for code comments
- Look at `src/prompts.py` for the extraction instructions

---

Happy email parsing! 🚀
