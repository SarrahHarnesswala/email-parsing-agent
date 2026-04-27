"""
Test suite for the email parsing agent.

These tests demonstrate how to use the EmailParserAgent with sample emails.
Each test case shows a different email type to test various parsing scenarios.

Run with: python -m pytest tests/test_parser.py -v
Or directly with: python tests/test_parser.py
"""

import sys
from pathlib import Path

# Add src directory to path so we can import the agent
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_parser import EmailParserAgent, parse_email
import json


# Sample test emails representing different scenarios
URGENT_REQUEST_EMAIL = """
From: boss@company.com
To: you@company.com
Date: April 27, 2026
Subject: URGENT: Q2 Budget Report Needed ASAP

Hi,

I need the Q2 budget report completed immediately. This is critical for the board meeting tomorrow morning.

Please:
1. Compile all department expenses from April-June
2. Generate the variance analysis
3. Create executive summary with key insights
4. Send me the final document by 11 PM tonight

This cannot wait. Let me know if you hit any blockers.

Thanks,
Sarah
"""


INFORMATIONAL_EMAIL = """
From: marketing@company.com
To: all-staff@company.com
Date: April 25, 2026
Subject: New Office Hours Starting Next Week

Team,

Just wanted to let everyone know that we're adjusting office hours starting next Monday, April 28th.

New office hours:
- Monday-Thursday: 8 AM - 5 PM
- Friday: 8 AM - 2 PM

The building will be closed on Fridays after 2 PM for maintenance. Please plan your schedules accordingly.

Best,
Marketing Team
"""


MEETING_REQUEST_EMAIL = """
From: client@external.com
To: you@company.com
Date: April 26, 2026
Subject: Project Discussion - Your Availability?

Hi there,

I hope this message finds you well. We'd like to discuss the upcoming project timeline with you.

Would you be available for a 30-minute call sometime next week? We're flexible with timing.

Some potential times that work for us:
- Tuesday 2-4 PM
- Wednesday 10-11 AM or 3-5 PM
- Thursday all day

Let me know what works best for you. We can do this over Zoom or phone.

Looking forward to connecting!

Best regards,
James Chen
CEO, TechVenture Inc.
"""


def test_urgent_email():
    """
    Test parsing an urgent email with explicit action items.

    This test demonstrates:
    - Extracting multiple action items from a list
    - Detecting high urgency from keywords (URGENT, immediately, cannot wait)
    - Identifying the main intent (complete a report)
    """
    print("\n" + "="*80)
    print("TEST 1: Urgent Email with Action Items")
    print("="*80)

    agent = EmailParserAgent()
    result = agent.parse_email(URGENT_REQUEST_EMAIL)

    print(f"\nParsed Email Data:")
    print(json.dumps(result.model_dump(), indent=2))

    # Verify critical fields
    assert result.sender == "boss@company.com", "Should extract sender correctly"
    assert "Budget Report" in result.subject, "Should extract subject"
    assert result.urgency_level == "high", "Should detect high urgency"
    assert len(result.action_items) > 0, "Should extract action items"

    print("\n✓ Test passed!")
    return result


def test_informational_email():
    """
    Test parsing an informational email with low urgency.

    This test demonstrates:
    - Extracting factual information
    - Detecting low urgency from neutral tone
    - Handling emails with no explicit action items
    """
    print("\n" + "="*80)
    print("TEST 2: Informational Email (Low Urgency)")
    print("="*80)

    agent = EmailParserAgent()
    result = agent.parse_email(INFORMATIONAL_EMAIL)

    print(f"\nParsed Email Data:")
    print(json.dumps(result.model_dump(), indent=2))

    # Verify critical fields
    assert result.sender == "marketing@company.com", "Should extract sender"
    assert "Office Hours" in result.subject, "Should extract subject"
    assert result.urgency_level == "low", "Should detect low urgency"

    print("\n✓ Test passed!")
    return result


def test_meeting_request_email():
    """
    Test parsing a professional meeting request.

    This test demonstrates:
    - Extracting time options as action items
    - Detecting medium urgency (polite but requests action)
    - Parsing structured email with date/time information
    """
    print("\n" + "="*80)
    print("TEST 3: Meeting Request Email")
    print("="*80)

    agent = EmailParserAgent()
    result = agent.parse_email(MEETING_REQUEST_EMAIL)

    print(f"\nParsed Email Data:")
    print(json.dumps(result.model_dump(), indent=2))

    # Verify critical fields
    assert result.sender == "client@external.com", "Should extract sender"
    assert "availability" in result.subject.lower(), "Should capture meeting context"
    assert len(result.action_items) > 0, "Should extract availability as action item"

    print("\n✓ Test passed!")
    return result


def run_all_tests():
    """Run all test cases and display results."""
    print("\n" + "🚀 " + "="*76 + " 🚀")
    print("EMAIL PARSING AGENT - TEST SUITE")
    print("🚀 " + "="*76 + " 🚀")

    try:
        test_urgent_email()
        test_informational_email()
        test_meeting_request_email()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\nThe email parser successfully:")
        print("  ✓ Extracted sender information")
        print("  ✓ Captured email subjects")
        print("  ✓ Identified main intent")
        print("  ✓ Extracted action items")
        print("  ✓ Classified urgency levels")

    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"\nError: {type(e).__name__}")
        print(f"Message: {str(e)}")
        raise


if __name__ == "__main__":
    run_all_tests()
