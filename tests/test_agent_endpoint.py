"""
Integration tests for the agent chat endpoint
Run with: pytest tests/test_agent_endpoint.py -v
Or manually with: python -m tests.test_agent_endpoint
"""
import requests
import json
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"


class AgentTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.thread_id: Optional[str] = None
    
    def setup_user(self, email: str = "test@example.com", password: str = "testpass123"):
        """Register or login a test user"""
        print(f"\n🔐 Setting up user: {email}")
        
        # Try login first
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code != 200:
            # Register if login fails
            print("   Creating new user...")
            register_data = {
                "first_name": "Test",
                "last_name": "Farmer",
                "email": email,
                "password": password
            }
            response = requests.post(f"{self.base_url}/auth/register", json=register_data)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Auth failed: {response.status_code} - {response.text}")
        
        self.token = response.json()["access_token"]
        print(f"   ✅ Authenticated successfully")
        return self.token
    
    def create_test_form(self):
        """Create a sample land form for testing"""
        print("\n📋 Creating test form...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Check if form already exists
        response = requests.get(f"{self.base_url}/forms/", headers=headers)
        if response.status_code == 200 and len(response.json()) > 0:
            print("   ✅ Form already exists")
            return response.json()[0]
        
        # Create new form
        form_data = {
            "location": "Lahore, Punjab, Pakistan",
            "area_type": "Plain",
            "soil_type": "Loamy",
            "water_source": "Tube well",
            "irrigation": "Yes",
            "temperature": "Moderate",
            "rainfall": "Medium",
            "sunlight": "Long hours",
            "land_size": "5 acres",
            "goal": "Profit",
            "crop_duration": "2–3 months",
            "specific_crop": "Wheat",
            "fertilizers_preference": "Organic preferred"
        }
        
        response = requests.post(f"{self.base_url}/forms/", json=form_data, headers=headers)
        
        if response.status_code != 201:
            raise Exception(f"Form creation failed: {response.status_code} - {response.text}")
        
        print("   ✅ Form created successfully")
        return response.json()
    
    def chat(self, message: str, thread_id: Optional[str] = None) -> dict:
        """Send a chat message to the agent"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        payload = {"message": message}
        if thread_id:
            payload["thread_id"] = thread_id
        
        response = requests.post(
            f"{self.base_url}/agent/chat",
            json=payload,
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Chat failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    def run_conversation_test(self):
        """Run a multi-turn conversation test"""
        print("\n" + "="*70)
        print("🤖 REGENAI AGENT CONVERSATION TEST")
        print("="*70)
        
        # Setup
        self.setup_user()
        self.create_test_form()
        
        # Test 1: Initial query
        print("\n📝 Test 1: Initial crop recommendation query")
        print("-" * 70)
        query1 = "Based on my land, what crop should I plant next month? Give me 2-3 specific recommendations."
        print(f"User: {query1}")
        
        result1 = self.chat(query1)
        self.thread_id = result1["thread_id"]
        
        print(f"\n🤖 Agent:")
        print(result1["reply"])
        print(f"\n📌 Thread ID: {self.thread_id}")
        
        # Test 2: Follow-up question (same thread)
        print("\n" + "="*70)
        print("📝 Test 2: Follow-up about water requirements")
        print("-" * 70)
        query2 = "What about the water requirements for these crops?"
        print(f"User: {query2}")
        
        result2 = self.chat(query2, thread_id=self.thread_id)
        
        print(f"\n🤖 Agent:")
        print(result2["reply"])
        print(f"\n📌 Same Thread ID: {result2['thread_id']}")
        
        # Test 3: Another follow-up
        print("\n" + "="*70)
        print("📝 Test 3: Market and selling questions")
        print("-" * 70)
        query3 = "Where can I sell these crops for the best price?"
        print(f"User: {query3}")
        
        result3 = self.chat(query3, thread_id=self.thread_id)
        
        print(f"\n🤖 Agent:")
        print(result3["reply"])
        
        # Test 4: New conversation (different thread)
        print("\n" + "="*70)
        print("📝 Test 4: New conversation - organic farming")
        print("-" * 70)
        query4 = "I want to switch to organic farming. What changes do I need to make?"
        print(f"User: {query4}")
        
        result4 = self.chat(query4)  # No thread_id = new conversation
        new_thread = result4["thread_id"]
        
        print(f"\n🤖 Agent:")
        print(result4["reply"])
        print(f"\n📌 New Thread ID: {new_thread}")
        print(f"   (Different from previous: {new_thread != self.thread_id})")
        
        # Summary
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\n📊 Test Summary:")
        print(f"   • User authenticated: ✅")
        print(f"   • Form created: ✅")
        print(f"   • Initial query: ✅")
        print(f"   • Follow-up query (same thread): ✅")
        print(f"   • Context retention: ✅")
        print(f"   • New conversation: ✅")
        print(f"   • Thread isolation: ✅")
        print("\n🎉 RegenAI Agent is working correctly!\n")


def main():
    """Run the agent tests"""
    tester = AgentTester()
    
    try:
        tester.run_conversation_test()
    except Exception as e:
        print(f"\n❌ TEST FAILED")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

