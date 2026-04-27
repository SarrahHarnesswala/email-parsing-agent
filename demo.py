#!/usr/bin/env python
"""
Demo script showing how to use the email parsing agent.

This script demonstrates the full workflow:
1. Create an agent instance
2. Parse sample emails
3. Display the extracted information
4. Show how to access individual fields

Run with: python demo.py
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.email_parser import EmailParserAgent, parse_email


def demo_basic_usage():
    """Demonstrate basic usage with a single email."""
    print("\n" + "="*80)
    print("DEMO 1: Basic Email Parsing")
    print("="*80)

    # A sample email
    sample_email = """
From: manager@company.com
To: team@company.com
Date: April 27, 2026
Subject: Important: Project Deadline Updated

Hi team,

I wanted to let you know that the project deadline has been moved up to next Friday.

Action items:
1. Review the updated timeline
2. Adjust sprint tasks accordingly
3. Schedule a sync meeting with the stakeholders

This is urgent, so please prioritize this.

Thanks,
Manager
"""

    print(f"\nInput Email:")
    print("-" * 80)
    print(sample_email)
    print("-" * 80)

    # Parse the email (simple function call)
    print("\n📧 Parsing email with local Ollama model (llama3.2)...")
    print("   (This may take a moment on first run as the model loads)")

    try:
        result = parse_email(sample_email)

        print("\n✅ Parsing successful!")
        print("\nExtracted Information:")
        print("-" * 80)
        print(f"Sender:         {result.sender}")
        print(f"Subject:        {result.subject}")
        print(f"Date:           {result.date}")
        print(f"Main Intent:    {result.main_intent}")
        print(f"Urgency Level:  {result.urgency_level}")
        print(f"Action Items:   {len(result.action_items)} item(s)")
        for i, item in enumerate(result.action_items, 1):
            print(f"  {i}. {item}")

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nMake sure Ollama is running:")
        print("  1. In a terminal: ollama serve")
        print("  2. In another terminal: ollama pull llama3.2")
        raise


def demo_json_output():
    """Demonstrate JSON output format."""
    print("\n" + "="*80)
    print("DEMO 2: JSON Output Format")
    print("="*80)

    sample_email = """
From: client@external.com
Subject: Quick Question

Hi, do you have time for a brief call this week?

Thanks
"""

    print(f"\nInput Email:")
    print(sample_email)

    print("\n📧 Parsing...")

    try:
        result = parse_email(sample_email)

        # Show as JSON
        json_output = result.model_dump_json(indent=2)
        print("\nJSON Output:")
        print(json_output)

        # Show that you can access as dict
        print("\nAs Python Dictionary:")
        print(json.dumps(result.model_dump(), indent=2))

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        raise


def demo_custom_agent():
    """Demonstrate creating an agent with custom settings."""
    print("\n" + "="*80)
    print("DEMO 3: Custom Agent Configuration")
    print("="*80)

    print("\nCreating agent with custom settings:")
    print("  - Model: llama3.2")
    print("  - Base URL: http://localhost:11434")
    print("  - Temperature: 0.3 (for consistency)")

    # Create a custom agent
    agent = EmailParserAgent(
        model_name="llama3.2",
        ollama_base_url="http://localhost:11434"
    )

    print("✅ Agent created successfully!")

    sample_email = """
From: support@service.com
Subject: Your ticket #12345 has been resolved

Your support ticket has been resolved. No further action needed.
"""

    print(f"\nSample Email:")
    print(sample_email)

    print("\n📧 Parsing with custom agent...")

    try:
        result = agent.parse_email(sample_email)

        print("\n✅ Parsed successfully!")
        print(f"Urgency:  {result.urgency_level}")
        print(f"Intent:   {result.main_intent}")
        print(f"Items:    {len(result.action_items)}")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        raise


def main():
    """Run all demos."""
    print("\n" + "🚀 " + "="*74 + " 🚀")
    print("EMAIL PARSING AGENT - DEMO")
    print("🚀 " + "="*74 + " 🚀")

    print("\nThis demo shows three ways to use the email parsing agent:")
    print("1. Basic usage with the convenience function")
    print("2. JSON output format")
    print("3. Custom agent configuration")

    print("\n⚠️  Prerequisites:")
    print("   - Ollama must be running: ollama serve")
    print("   - llama3.2 model must be installed: ollama pull llama3.2")

    input("\n\nPress Enter to start the demos...")

    try:
        demo_basic_usage()
        demo_json_output()
        demo_custom_agent()

        print("\n" + "="*80)
        print("✅ All demos completed successfully!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Run the test suite: python tests/test_parser.py")
        print("  2. Try parsing your own emails")
        print("  3. Check README.md for more advanced usage")

    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Demo failed: {type(e).__name__}")
        print(f"Please ensure Ollama is running and accessible")
        sys.exit(1)


if __name__ == "__main__":
    main()
