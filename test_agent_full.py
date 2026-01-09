#!/usr/bin/env python
"""
Agent Functionality Test (RATE-LIMIT SAFE)
"""

import time
import json
from Backend.agent import get_agent

print("=" * 70)
print("HCLTech Enterprise Agent - Full Functionality Test")
print("=" * 70)

agent = get_agent()
print(f"✅ Agent initialized: {type(agent).__name__}")

# -------------------- TEST 1 --------------------
print("\n" + "=" * 70)
print("TEST 1: Issue Detection")
print("=" * 70)

test_cases = [
    ("What was the revenue in 2024?", "QUERY"),
    ("The login system is broken", "ISSUE"),
    ("Schedule a meeting with HR", "ISSUE"),
    ("What are the company policies?", "QUERY"),
]

for query, expected in test_cases:
    print(f"\n📝 Input: {query}")
    print(f"Expected: {expected}")

    try:
        result = agent.invoke(query)
        print(f"Response: {result['output'][:100]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")

    time.sleep(3)  # 🔑 RATE LIMIT PROTECTION

# -------------------- TEST 2 --------------------
print("\n" + "=" * 70)
print("TEST 2: Confirmation Flow")
print("=" * 70)

agent2 = get_agent()

print("\n📝 Input: Database is down")
res1 = agent2.invoke("Database is down")
print(res1["output"])

time.sleep(2)

print("\n📝 User: no")
res2 = agent2.invoke("no")
print(res2["output"])

# -------------------- TEST 3 --------------------
print("\n" + "=" * 70)
print("TEST 3: Tools")
print("=" * 70)

from Backend.tools import create_it_ticket, schedule_meeting

ticket = create_it_ticket("Test issue", "Tester", "test@mail.com")
print(json.dumps(ticket, indent=2))

meeting = schedule_meeting("HR", "Test meeting", "Tester", "test@mail.com")
print(json.dumps(meeting, indent=2))

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETED SAFELY")
print("=" * 70)
