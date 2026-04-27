# CLAUDE.md

This file provides guidance to Claude Code when working with this project.

## Project Overview

**Email Parsing Agent** — A Python application that uses Ollama (llama3.2) and LangChain to extract structured information from raw email text.

**Problem solved**: Unstructured emails → Structured JSON with extracted fields (sender, subject, main intent, action items, urgency level)

**Architecture**: Uses a local LLM (Ollama + llama3.2) with prompt engineering to guide consistent, structured output instead of naive regex-based parsing.

---

## Tech Stack

- **Python 3.9+** — Primary language
- **LangChain 1.2.15** — Framework for chaining prompts, LLMs, and processing pipelines (moved from `langchain.*` to `langchain_core.*` imports in v1.0+)
- **langchain-core 1.3.2** — Core LangChain abstractions (PromptTemplate, message types, etc.)
- **langchain-ollama 1.1.0** — Integration layer for Ollama LLM backend
- **Ollama** — Runs LLMs locally on port 11434 (external service, must run separately)
- **llama3.2 (3.2B parameters)** — Default LLM model (runs in Ollama)
- **Pydantic 2.13.3** — Type validation and structured data models (EmailData)
- **python-dotenv 1.2.2** — Environment variable management
- **ollama 0.6.1** — Python client library for Ollama API

**Future**: FastAPI planned for REST API endpoints.

---

## Project Structure

```
email-agent/
├── src/
│   ├── __init__.py
│   ├── email_parser.py         # Main agent implementation
│   │   ├── EmailParserAgent    # Class: orchestrates LLM calls, JSON parsing, validation
│   │   ├── EmailData           # Pydantic model: structured output schema
│   │   └── parse_email()       # Function: convenience wrapper with defaults
│   └── prompts.py              # LLM prompt templates
│       └── EMAIL_PARSING_PROMPT # String template with extraction instructions
│
├── tests/
│   ├── __init__.py
│   └── test_parser.py          # Test suite with 3 representative email scenarios
│       ├── test_urgent_email()
│       ├── test_informational_email()
│       └── test_meeting_request_email()
│
├── demo.py                      # Interactive demo showing 3 usage patterns
├── requirements.txt             # Pinned dependencies (install with: pip install -r requirements.txt)
├── .env.example                 # Environment template (copy to .env for local setup)
├── README.md                    # User-facing documentation
├── CLAUDE.md                    # This file (guidance for Claude Code)
└── venv/                        # Python virtual environment (created at setup)
```

### File Responsibilities

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `src/email_parser.py` | Core agent logic | `EmailParserAgent`, `EmailData`, `parse_email()` |
| `src/prompts.py` | LLM instructions | `EMAIL_PARSING_PROMPT` (string) |
| `tests/test_parser.py` | Verification | 3 test functions covering urgent/informational/meeting emails |
| `demo.py` | User-facing examples | 3 demo functions showing basic/JSON/custom usage |

---

## How to Run the Project

### Prerequisites

1. **Python 3.9+** installed
2. **Ollama running** (separate process on port 11434)
3. **llama3.2 model** downloaded in Ollama

### Step 1: Start Ollama

In a terminal:
```bash
ollama serve
```

In another terminal (one-time setup):
```bash
ollama pull llama3.2
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### Step 2: Activate Virtual Environment

**Windows (bash/Git Bash):**
```bash
cd C:\Users\HP\Desktop\Agent_Practice\ 2\email-agent
source venv/Scripts/activate
```

**Windows (cmd.exe):**
```cmd
cd C:\Users\HP\Desktop\Agent_Practice 2\email-agent
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
cd "C:\Users\HP\Desktop\Agent_Practice 2\email-agent"
venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Run the Project

```bash
# Run interactive demo (shows 3 usage patterns)
python demo.py

# Run test suite (runs 3 representative email scenarios)
python -m pytest tests/test_parser.py -v
# OR (direct python, no pytest required)
python tests/test_parser.py

# Use in Python code
python -c "from src.email_parser import parse_email; result = parse_email('From: test@example.com\nSubject: Hello\n\nBody'); print(result.sender)"
```

---

## Common Commands

```bash
# Activate environment
source venv/Scripts/activate  # bash/Git Bash on Windows
venv\Scripts\activate.bat     # cmd.exe on Windows

# Run tests
python tests/test_parser.py
python -m pytest tests/test_parser.py -v

# Run demo
python demo.py

# Check Ollama connection
curl http://localhost:11434/api/tags

# List available models in Ollama
ollama list

# Pull a different model
ollama pull llama2
ollama pull neural-chat

# Deactivate environment
deactivate
```

---

## Known Issues and Fixes

### Issue 1: `ModuleNotFoundError: No module named 'langchain.prompts'`

**Root cause**: LangChain 1.0+ reorganized imports. `langchain.prompts` and `langchain.chains` no longer exist.

**Fix**: Use `langchain_core` instead:
```python
# OLD (broken in v1.0+)
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# NEW (correct for v1.2.15)
from langchain_core.prompts import PromptTemplate
# Use pipe operator instead of LLMChain: prompt | llm
```

**Files affected**: `src/email_parser.py` (already fixed)

---

### Issue 2: `ModuleNotFoundError: No module named 'langchain_ollama'` when running without venv

**Root cause**: Dependencies installed in `venv/` are not accessible without activation.

**Fix**: Always activate the virtual environment first:
```bash
source venv/Scripts/activate  # Windows bash
venv\Scripts\activate.bat     # Windows cmd
source venv/bin/activate      # macOS/Linux
```

---

### Issue 3: `AttributeError: 'str' object has no attribute 'content'`

**Root cause**: OllamaLLM returns a plain string, not an AIMessage object. The pipe operator syntax (`prompt | llm`) returns the string directly.

**Fix**: Handle both string and AIMessage responses:
```python
# In src/email_parser.py, line 109
response_text = response if isinstance(response, str) else response.content
```

**Files affected**: `src/email_parser.py` (already fixed)

---

### Issue 4: `UnicodeEncodeError` with emoji in output

**Root cause**: Windows default terminal encoding is cp1252, can't display emoji.

**Workaround**: Use UTF-8 encoding or run with PYTHONIOENCODING:
```bash
PYTHONIOENCODING=utf-8 python demo.py
```

**Note**: Not critical; the code runs fine, just emoji don't display in Windows cmd/PowerShell.

---

### Issue 5: Ollama service not found at localhost:11434

**Root cause**: Ollama not running or listening on a different host.

**Fix**:
```bash
# Start Ollama
ollama serve

# Check it's running
curl http://localhost:11434/api/tags

# If on a different machine, use the host/port in EmailParserAgent:
agent = EmailParserAgent(ollama_base_url="http://192.168.1.100:11434")
```

---

## Coding Conventions

### Imports

1. **Order**: External libraries first, then relative imports
   ```python
   import json
   import os
   from pydantic import BaseModel
   from langchain_core.prompts import PromptTemplate
   from .prompts import EMAIL_PARSING_PROMPT
   ```

2. **LangChain imports**: Use `langchain_core.*` and provider-specific packages (e.g., `langchain_ollama`), NOT `langchain.*`
   ```python
   from langchain_core.prompts import PromptTemplate
   from langchain_ollama import OllamaLLM
   # NOT: from langchain.prompts import PromptTemplate
   ```

### Type Hints

- **All function signatures** must include type hints
- **Pydantic models** define field types with Field() descriptions
- **Optional types** explicitly use `Optional[str]` or `T | None`

```python
def parse_email(email_text: str) -> EmailData:
    """Parse email and return structured data."""
    ...

class EmailData(BaseModel):
    sender: str = Field(description="Email address of sender")
    date: Optional[str] = Field(default=None, description="Send date")
```

### Naming Conventions

| Category | Convention | Example |
|----------|-----------|---------|
| Classes | PascalCase | `EmailParserAgent`, `EmailData` |
| Functions/Methods | snake_case | `parse_email()`, `invoke()` |
| Constants | UPPER_SNAKE_CASE | `EMAIL_PARSING_PROMPT` |
| Private/Internal | `_prefix` | `_helper_function()` |
| Module names | snake_case | `email_parser.py`, `prompts.py` |

### Comments

- **Default**: No comments. Code should be self-explanatory via naming.
- **When to comment**: Only explain the WHY for non-obvious behavior
  - Workarounds for specific bugs
  - Subtle invariants or constraints
  - Design decisions with tradeoffs
  
```python
# Good: explains WHY
temperature=0.3  # Lower temp reduces hallucinations for JSON extraction

# Bad: explains WHAT (the code already says this)
response_text = response.strip()  # Remove whitespace

# Good: explains non-obvious behavior
# OllamaLLM returns str, not AIMessage, so we check isinstance
response_text = response if isinstance(response, str) else response.content
```

### Docstrings

- **Module level**: Explain purpose and data flow (2-3 sentences)
- **Classes**: Explain responsibility and key components
- **Methods/Functions**: Explain parameters, return type, and exceptions
- **Inline comments**: Explain non-obvious implementation details (one line max)

```python
def parse_email(email_text: str) -> EmailData:
    """
    Parse raw email and extract structured information.
    
    Process:
    1. Format prompt with email text
    2. Invoke OllamaLLM via prompt | llm chain
    3. Clean markdown code blocks from response
    4. Parse JSON into dictionary
    5. Validate against EmailData schema
    
    Args:
        email_text: Raw email content as string
    
    Returns:
        EmailData: Validated structured email data
    
    Raises:
        json.JSONDecodeError: If LLM response is not valid JSON
        ValueError: If extracted data doesn't match schema
    """
    ...
```

### Error Handling

- **At system boundaries** (user input, external APIs): Validate and provide clear errors
- **Internal code**: Trust framework/library guarantees, no defensive checks
- **Don't add error handling** for scenarios that can't happen

```python
# Good: validate at boundary (LLM output)
try:
    parsed_data = json.loads(response_text)
except json.JSONDecodeError as e:
    raise ValueError(f"LLM returned invalid JSON: {response_text}") from e

# Bad: defensive checks for impossible scenarios
if self.llm is None:  # Can't happen - we set it in __init__
    raise RuntimeError("LLM not initialized")
```

### Code Organization

- **One responsibility per class/function**: EmailParserAgent orchestrates, EmailData validates
- **Avoid premature abstraction**: Three similar lines are better than a generic helper
- **No half-finished implementations**: Either complete the feature or don't ship it
- **No feature flags for incomplete work**: If code is ready, enable it; if not, don't ship

---

## Architecture Details

### Data Flow

```
User Email Text
    ↓
PromptTemplate.format(email_text="...")
    ↓
Pipe to OllamaLLM (sends to http://localhost:11434)
    ↓
LLM generates JSON response
    ↓
Clean markdown blocks (if present)
    ↓
json.loads() → Python dict
    ↓
EmailData(**dict) → Pydantic validation
    ↓
EmailData object (fully validated)
```

### Key Design Decisions

1. **Prompt-driven extraction** — LLM understands context better than regex. More flexible.
2. **Pydantic validation layer** — Catches malformed LLM output immediately. Clear error messages.
3. **Local-only execution** — Ollama runs locally on port 11434. No cloud APIs, no API keys, all data stays local.
4. **Temperature=0.3** — Low temperature keeps outputs consistent and factual.
5. **Pipe operator over LLMChain** — Modern LangChain syntax, simpler and more composable.

---

## Testing Strategy

Tests in `tests/test_parser.py` verify:
- ✓ Correct extraction of email fields (sender, subject, date)
- ✓ Correct intent classification
- ✓ Correct urgency level detection (high/medium/low)
- ✓ Correct action item extraction

Tests are **representative, not exhaustive**:
- 3 test cases covering different email types (urgent, informational, meeting request)
- Not edge-case focused
- For custom emails, run `demo.py` and verify manually

**Running tests**:
```bash
python tests/test_parser.py
# OR
python -m pytest tests/test_parser.py -v
```

---

## Performance Notes

- **First inference**: ~60-120 seconds (model loads into memory once)
- **Subsequent inferences**: ~2-10 seconds (depends on email length)
- **Optimization**: Use smaller models (llama2) if speed is critical
- **Bottleneck**: Network to Ollama service; increase num_predict if truncating responses

---

## Future Work

- **FastAPI REST endpoint** — Expose as HTTP API (planned)
- **Batch processing** — Handle multiple emails efficiently
- **Custom models** — Support user-provided Ollama models
- **Async inference** — Non-blocking LLM calls
- **Persistent storage** — Save results to database
- **Web UI** — Interactive email analyzer

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot connect to Ollama` | Service not running | `ollama serve` in a terminal |
| `llama3.2 model not found` | Model not downloaded | `ollama pull llama3.2` |
| `No module named 'langchain.prompts'` | Old import path | Use `langchain_core.prompts` |
| `AttributeError: 'str' object has no attribute 'content'` | Response type mismatch | Use `isinstance(response, str)` check |
| `UnicodeEncodeError` with emoji | Windows terminal encoding | Use `PYTHONIOENCODING=utf-8` |
| Slow inference | Normal on first run | Model loads once, subsequent calls are faster |

---

## Resources

- **LangChain docs**: https://python.langchain.com
- **Ollama docs**: https://ollama.ai
- **Pydantic docs**: https://docs.pydantic.dev
- **llama3.2 model**: https://ollama.ai/library/llama3.2

---

## Quick Reference

```bash
# Setup (one time)
cd email-agent && python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
ollama pull llama3.2

# Development (every session)
source venv/Scripts/activate  # Windows bash
ollama serve                  # In another terminal
python demo.py                # Run demo
python tests/test_parser.py   # Run tests

# Deactivate when done
deactivate
```

---

**Last Updated**: April 27, 2026  
**Python Version**: 3.9+  
**LangChain Version**: 1.2.15  
**Key Dependencies**: langchain, langchain-core, langchain-ollama, pydantic
