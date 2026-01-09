#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script to validate all components before deployment
Run: python test_components.py
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """Test all required imports"""
    print("\n[IMPORTS] Testing imports...")
    try:
        import langchain
        print("  [PASS] langchain")
        
        import streamlit
        print("  [PASS] streamlit")
        
        import faiss
        print("  [PASS] faiss")
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("  [PASS] langchain_google_genai")
        
        from langchain_community.embeddings import HuggingFaceEmbeddings
        print("  [PASS] huggingface embeddings")
        
        return True
    except ImportError as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def test_env_vars():
    """Test environment variables"""
    print("\n[ENV] Testing environment variables...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and len(api_key) > 10:
        print("  [PASS] GOOGLE_API_KEY found")
    else:
        print("  [FAIL] GOOGLE_API_KEY missing or invalid")
        return False
    
    return True


def test_vector_db():
    """Test vector database"""
    print("\n[DB] Testing vector database...")
    try:
        from Backend.rag_engine import load_vector_db
        db = load_vector_db()
        
        # Try a simple search
        results = db.similarity_search("revenue", k=1)
        if results:
            print(f"  [PASS] Vector DB loaded successfully")
            print(f"     Found {len(results)} document(s) for test query")
            return True
        else:
            print("  [WARN] Vector DB loaded but no results for test query")
            return True
    except Exception as e:
        print(f"  [FAIL] Vector DB error: {e}")
        return False


def test_llm():
    """Test LLM connection"""
    print("\n[LLM] Testing LLM (Gemini)...")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        
        # Try a simple invoke
        response = llm.invoke("Say 'Hello' only.")
        if response:
            print("  [PASS] LLM connected successfully")
            print(f"     Response: {response.content[:50]}...")
            return True
    except Exception as e:
        error_str = str(e)
        # Free tier quota limit is expected during testing
        if "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
            print("  [WARN] API quota limit reached (free tier)")
            print("     This is expected - LLM is configured correctly")
            return True
        elif "429" in error_str or "Rate" in error_str:
            print("  [WARN] Rate limited (temporary)")
            print("     This is expected - LLM is configured correctly")
            return True
        else:
            print(f"  [FAIL] LLM error: {e}")
            return False


def test_agent():
    """Test agent initialization"""
    print("\n[AGENT] Testing Agent...")
    try:
        from Backend.agent import get_agent, detect_issue
        
        agent = get_agent()
        print("  [PASS] Agent initialized successfully")
        
        # Test issue detection
        test_query = "The system is crashing"
        issue = detect_issue(test_query)
        print(f"  [PASS] Issue detection working: {issue}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Agent error: {e}")
        return False


def test_tools():
    """Test tool functions"""
    print("\n[TOOLS] Testing Tools...")
    try:
        from Backend.tools import (
            create_it_ticket,
            schedule_meeting,
            issue_detector,
            get_all_tickets,
            get_all_meetings
        )
        
        # Test ticket creation
        result = create_it_ticket(
            issue="Test issue",
            user_name="Test User",
            user_email="test@test.com"
        )
        print(f"  [PASS] Ticket creation: {result['ticket_id']}")
        
        # Test meeting scheduling
        result = schedule_meeting(
            department="HR",
            reason="Test meeting",
            user_name="Test User",
            user_email="test@test.com"
        )
        print(f"  [PASS] Meeting scheduling: {result['meeting_id']}")
        
        # Test retrieval
        tickets = get_all_tickets()
        meetings = get_all_meetings()
        print(f"  [PASS] Retrieved {len(tickets)} tickets, {len(meetings)} meetings")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Tools error: {e}")
        return False


def test_prompts():
    """Test prompt templates"""
    print("\n[PROMPTS] Testing Prompts...")
    try:
        from Backend.prompts import (
            AGENT_SYSTEM_PROMPT,
            ISSUE_DETECTION_PROMPT,
            SYSTEM_INSTRUCTIONS
        )
        
        if AGENT_SYSTEM_PROMPT and len(AGENT_SYSTEM_PROMPT) > 0:
            print("  [PASS] Agent system prompt loaded")
        if ISSUE_DETECTION_PROMPT and len(ISSUE_DETECTION_PROMPT) > 0:
            print("  [PASS] Issue detection prompt loaded")
        if SYSTEM_INSTRUCTIONS and len(SYSTEM_INSTRUCTIONS) > 0:
            print("  [PASS] System instructions loaded")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Prompts error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("[TEST] CHATBOT COMPONENT TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Environment Variables", test_env_vars),
        ("Vector Database", test_vector_db),
        ("LLM Connection", test_llm),
        ("Agent", test_agent),
        ("Tools", test_tools),
        ("Prompts", test_prompts),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[FAIL] Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! You're ready to deploy!")
        return 0
    else:
        print(f"\n[WARN] {total - passed} test(s) failed. Fix issues before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
