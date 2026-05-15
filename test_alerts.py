"""Test script to verify get_urgent_alerts tool works correctly."""

from mcp_server import get_urgent_alerts
import json

print("\nFetching unread emails and checking for urgent alerts...\n")

result = json.loads(get_urgent_alerts(10))

print("\n" + "="*60)
print("JSON Result:")
print("="*60)
print(json.dumps(result, indent=2))
