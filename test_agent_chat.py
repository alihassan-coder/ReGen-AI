"""
Test script for the ReGenAI agent with different conversation types
Run this to test the agent's conversational abilities
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# You need to login first to get a token
def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "your_email@example.com",  # Replace with your email
            "password": "your_password"  # Replace with your password
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def test_agent_chat(token, message, thread_id="test_01"):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "message": message,
        "thread_id": thread_id
    }
    
    print(f"\n{'='*60}")
    print(f"USER: {message}")
    print(f"{'='*60}")
    
    response = requests.post(
        f"{BASE_URL}/agent/chat",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nAGENT: {result['reply']}\n")
        return result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("ReGenAI Agent Conversation Test")
    print("="*60)
    
    # Get authentication token
    token = login()
    if not token:
        print("Please update the login credentials in the script")
        exit(1)
    
    # Test different conversation types
    thread_id = "test_conversation_01"
    
    # Test 1: Greeting
    test_agent_chat(token, "Hi! How are you?", thread_id)
    
    # Test 2: Ask about the agent
    test_agent_chat(token, "What can you do? Tell me about yourself.", thread_id)
    
    # Test 3: Farming question
    test_agent_chat(token, "What crops should I plant this season?", thread_id)
    
    # Test 4: Follow-up question (tests conversation memory)
    test_agent_chat(token, "What about irrigation for those crops?", thread_id)
    
    # Test 5: Casual conversation
    test_agent_chat(token, "Thank you! That's very helpful.", thread_id)
    
    print("\n" + "="*60)
    print("Test completed!")
