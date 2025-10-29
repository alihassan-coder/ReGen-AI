#!/usr/bin/env python3
"""
Quick test script to verify agent is working
"""

import sys
from agent.main_agent import get_agent

def test_agent():
    print("Testing ReGenAI Agent...")
    print("=" * 60)
    
    try:
        # Get agent instance
        print("1. Initializing agent...")
        agent = get_agent()
        print("✅ Agent initialized successfully")
        print()
        
        # Test with a simple message
        print("2. Testing agent response...")
        state = {
            "user_id": 1,
            "form": {
                "location": "Faisalabad, Punjab",
                "soil_type": "Loamy",
                "land_size": "5 acres",
                "goal": "Profit"
            },
            "message": "What crops should I plant?"
        }
        
        result = agent.invoke(state, {"configurable": {"thread_id": "test_123"}})
        
        if "reply" in result and result["reply"]:
            print("✅ Agent responded successfully!")
            print()
            print("Response:")
            print("-" * 60)
            print(result["reply"])
            print("-" * 60)
            print()
            print("✅ All tests passed! Agent is working correctly.")
            return 0
        else:
            print("❌ Agent returned empty response")
            print(f"Result: {result}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Common fixes:")
        print("1. Check GEMINI_API_KEY_ALI is set in .env")
        print("2. Verify API key is valid")
        print("3. Check internet connection")
        return 1

if __name__ == "__main__":
    sys.exit(test_agent())
