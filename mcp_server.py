"""
MCP server exposing Gmail inbox tools via the email parsing agent.

Tools exposed:
  - check_inbox(limit) — fetch and parse unread Gmail emails, return JSON summary
  - get_urgent_alerts(limit) — same, plus print alert banners for high-urgency emails

Usage:
  Run directly: python mcp_server.py
  Via MCP runtime: registered in .mcp.json, Claude Code will discover and use it
"""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure src/ is importable when running from email-agent/ root
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP
from src.email_parser import EmailParserAgent, EmailData
from src.gmail_client import GmailClient

load_dotenv()

# Single shared parser agent — reuse the LLM connection across tool calls
_parser = EmailParserAgent(
    model_name=os.getenv("OLLAMA_MODEL", "llama3.2"),
    ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)

mcp = FastMCP("email-agent")


def _fetch_and_parse(limit: int) -> tuple[list[dict], str | None]:
    """
    Shared fetch+parse pipeline for both tools.

    Connects to Gmail, fetches unread emails, and parses each with EmailParserAgent.
    Per-email parse failures are recorded in the "parse_error" field without
    aborting the batch.

    Returns:
        (results, error_message)
        - results: list of dicts, each containing EmailData fields + uid + parse_error
        - error_message: None on success, or a string describing connection/auth failures
    """
    results = []

    try:
        with GmailClient() as client:
            raw_emails = client.fetch_unread_emails(limit=limit)
    except KeyError as e:
        return [], f"Missing environment variable: {e}"
    except OSError as e:
        return [], f"Network connection failed: {e}"
    except Exception as e:
        # imaplib.IMAP4.error and other IMAP errors inherit from Exception
        return [], f"Gmail connection error: {type(e).__name__}: {e}"

    for raw in raw_emails:
        try:
            parsed: EmailData = _parser.parse_email(raw.raw_text)

            # Let Pydantic define the shape — don't rewrite it manually
            entry = parsed.model_dump()

            # Add IMAP-only fields that EmailData doesn't have
            entry["uid"] = raw.uid
            entry["parse_error"] = None

            # Prefer LLM-parsed date, fall back to IMAP date
            if not entry.get("date"):
                entry["date"] = raw.imap_date or ""

        except json.JSONDecodeError as e:
            # Parsing failed — use raw IMAP data as fallback
            entry = {
                "uid": raw.uid,
                "sender": raw.imap_from or "",  # fallback: IMAP header
                "subject": "",
                "date": raw.imap_date or "",    # fallback: IMAP header
                "main_intent": "",
                "action_items": [],
                "urgency_level": "low",         # valid Pydantic value
                "parse_error": f"LLM returned invalid JSON: {str(e)[:100]}",
            }
        except Exception as e:
            entry = {
                "uid": raw.uid,
                "sender": raw.imap_from or "",
                "subject": "",
                "date": raw.imap_date or "",
                "main_intent": "",
                "action_items": [],
                "urgency_level": "low",         # valid Pydantic value
                "parse_error": f"Parse failed: {type(e).__name__}: {str(e)[:100]}",
            }

        results.append(entry)

    return results, None


def _print_urgent_alert(entry: dict) -> None:
    """
    Print a visual alert banner for a high-urgency email to stderr.

    Writes to stderr because the MCP stdio transport uses stdout exclusively
    for JSON-RPC protocol messages. Any non-JSON-RPC text on stdout corrupts
    the protocol stream.
    """
    banner = "=" * 60
    sys.stderr.write(f"{banner}\n")
    sys.stderr.write("*** URGENT EMAIL ALERT ***\n")
    sys.stderr.write(f"UID:     {entry['uid']}\n")
    sys.stderr.write(f"From:    {entry['sender']}\n")
    sys.stderr.write(f"Subject: {entry['subject']}\n")
    sys.stderr.write(f"Intent:  {entry['main_intent']}\n")
    if entry['action_items']:
        sys.stderr.write("Actions:\n")
        for i, item in enumerate(entry['action_items'], 1):
            sys.stderr.write(f"  {i}. {item}\n")
    sys.stderr.write(f"{banner}\n")
    sys.stderr.flush()


@mcp.tool()
def check_inbox(limit: int = 10) -> str:
    """
    Fetch and parse unread emails from Gmail inbox.

    Connects to Gmail via IMAP, retrieves up to `limit` most recent unread
    emails, parses each with the local Ollama LLM, and returns a JSON summary.

    Args:
        limit: Maximum number of unread emails to fetch (default 10, max 50).

    Returns:
        JSON string with structure:
        {
          "total_fetched": <int>,
          "emails": [
            {
              "uid": "<imap_uid>",
              "sender": "...",
              "subject": "...",
              "date": "...",
              "main_intent": "...",
              "action_items": [...],
              "urgency_level": "high|medium|low",
              "parse_error": null | "<error message>"
            },
            ...
          ]
        }

        On connection/auth failure, returns:
        {"error": "<error message>", "total_fetched": 0, "emails": []}
    """
    results, error = _fetch_and_parse(limit)

    if error:
        return json.dumps({
            "error": error,
            "total_fetched": 0,
            "emails": [],
        })

    return json.dumps({
        "total_fetched": len(results),
        "emails": results,
    }, indent=2)


@mcp.tool()
def get_urgent_alerts(limit: int = 10) -> str:
    """
    Fetch unread emails and alert on high-urgency messages.

    Same fetch-and-parse pipeline as check_inbox, but additionally prints
    visual alert banners to stderr for every email with urgency_level == "high".

    Args:
        limit: Maximum number of unread emails to fetch (default 10, max 50).

    Returns:
        JSON string with structure:
        {
          "total_fetched": <int>,
          "urgent_count": <int>,
          "urgent_emails": [
            {
              "uid": "...",
              "sender": "...",
              "subject": "...",
              "urgency_level": "high",
              "action_items": [...]
            }
          ],
          "all_emails": [ ... same schema as check_inbox ... ]
        }

        On connection/auth failure, returns:
        {"error": "<error message>", "total_fetched": 0, "urgent_count": 0, "urgent_emails": [], "all_emails": []}
    """
    results, error = _fetch_and_parse(limit)

    if error:
        return json.dumps({
            "error": error,
            "total_fetched": 0,
            "urgent_count": 0,
            "urgent_emails": [],
        })

    urgent = [r for r in results if r["urgency_level"] == "high"]

    for entry in urgent:
        _print_urgent_alert(entry)

    return json.dumps({
        "total_fetched": len(results),
        "urgent_count": len(urgent),
        "urgent_emails": urgent,
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
