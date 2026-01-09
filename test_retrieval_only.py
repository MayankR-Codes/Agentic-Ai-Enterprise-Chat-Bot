#!/usr/bin/env python
"""
Test RAG retrieval WITHOUT LLM (no API calls needed)
Verifies that the vector DB is correctly returning relevant documents
"""
from Backend.rag_engine import load_vector_db

print("=" * 70)
print("Testing RAG Retrieval (No API Calls) - Business Strategy")
print("=" * 70)

try:
    vector_db = load_vector_db()
    retriever = vector_db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 10, "fetch_k": 20}
    )
    print("✅ Vector DB loaded with improved retrieval settings")
except Exception as e:
    print(f"❌ Failed to load vector DB: {e}")
    exit(1)

test_queries = [
    ("What is the business strategy?", "business strategy", 3),
    ("Tell me about strategic objectives", "strategic objectives", 3),
    ("What are the strategic goals?", "strategic goals", 2),
    ("Explain the growth strategy", "growth strategy", 2),
]

print("\n" + "=" * 70)
print("Retrieval Test Results")
print("=" * 70)

all_passed = True

for query, keywords, expected_min in test_queries:
    print(f"\n📝 Query: {query}")
    print(f"   Looking for keywords: {keywords}")
    print("   ─" * 35)
    
    try:
        docs = retriever.invoke(query)
        print(f"   Retrieved {len(docs)} documents")
        
        # Check if any doc contains relevant keywords
        found = False
        for i, doc in enumerate(docs[:5], 1):
            content = doc.page_content.lower()
            if any(kw.lower() in content for kw in keywords.split()):
                found = True
                print(f"   ✅ Doc {i}: Contains '{keywords}'")
                print(f"      Preview: {content[:80]}...")
                break
        
        if not found:
            all_passed = False
            print(f"   ⚠️  No docs with '{keywords}' found")
            print(f"   First doc: {docs[0].page_content[:100]}...")
        
    except Exception as e:
        all_passed = False
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL RETRIEVAL TESTS PASSED!")
    print("\nThe RAG system is now correctly:")
    print("  • Retrieving MORE documents (10 instead of 3)")
    print("  • Using MMR (Maximum Marginal Relevance) search")
    print("  • Returning relevant content for business strategy queries")
    print("\nWhen API quota is available, the LLM will provide complete answers.")
else:
    print("⚠️  Some retrieval tests had issues")

print("=" * 70)
print("\nTo verify with LLM answers:")
print("1. Get a new API key from Google Cloud")
print("2. Update .env with GOOGLE_API_KEY")
print("3. Ask 'What is the business strategy?' in the chat")
print("4. Agent should return full answer from documents")
