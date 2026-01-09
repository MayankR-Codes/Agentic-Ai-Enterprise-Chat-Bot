#!/usr/bin/env python
"""
Test the fixed RAG system with business strategy queries
"""
from Backend.agent import get_agent

print("=" * 70)
print("Testing Improved RAG System - Business Strategy Queries")
print("=" * 70)

agent = get_agent()

test_queries = [
    "What is the business strategy of HCLTech?",
    "Tell me about the strategic framework",
    "What are the strategic objectives?",
    "What is the medium-term strategy?",
    "How does HCLTech approach growth?",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'─' * 70}")
    print(f"Test {i}: {query}")
    print('─' * 70)
    
    try:
        result = agent.invoke(query)
        response = result.get("output", "No response")
        
        # Check if response contains actual content
        if "Information not found" in response or "not found in" in response:
            print("❌ FAILED: 'Information not found'")
            print(f"Response: {response[:200]}")
        elif len(response) > 100:
            print("✅ SUCCESS: Found relevant content")
            print(f"Response: {response[:300]}...")
        else:
            print("⚠️  WARNING: Short response")
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:200]}")

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)
print("""
✅ If all tests show "SUCCESS", the RAG system is working correctly!
⚠️  If some show "FAILED", you may need to:")
   1. Wait for API quota to reset
   2. Check if new API key has available quota
   3. Try simpler queries
""")
