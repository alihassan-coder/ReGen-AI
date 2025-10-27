import asyncio
import uuid
from datetime import datetime
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
from config.env_config import EnvironmentConfig
from config.memory_config import memory_manager
from agent.tools import (
    get_weather_data, 
    get_air_quality_data, 
    calculate_carbon_footprint,
    get_climate_actions,
    get_eco_tips_by_season
)

class ReGenAI:
    """ReGenAI - AI Climate Action Agent"""
    
    def __init__(self):
        self.setup_client()
        self.setup_agent()
        self.user_id = None
    
    def setup_client(self):
        """Setup OpenAI client with API key"""
        api_key = EnvironmentConfig.OPENAI_API_KEY or EnvironmentConfig.GEMINI_API_KEY
        
        if not api_key:
            raise ValueError("No API key found. Please set OPENAI_API_KEY or GEMINI_API_KEY")
        
        # Use Gemini if GEMINI_API_KEY is available, otherwise use OpenAI
        if EnvironmentConfig.GEMINI_API_KEY:
            self.client = AsyncOpenAI(
                api_key=EnvironmentConfig.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            self.model_name = "gemini-2.0-flash"
        else:
            self.client = AsyncOpenAI(api_key=EnvironmentConfig.OPENAI_API_KEY)
            self.model_name = "gpt-4"
    
    def setup_agent(self):
        """Setup the ReGenAI agent with climate-focused instructions and tools"""
        instructions = """
        You are ReGenAI, an AI Climate Action Agent dedicated to helping people make environmentally conscious decisions and take meaningful climate action.

        Your mission:
        - Analyze local weather and air quality data to provide personalized climate recommendations
        - Calculate carbon footprints for various activities
        - Suggest practical, actionable steps to reduce environmental impact
        - Provide seasonal eco-friendly tips and advice
        - Help users understand the environmental impact of their choices

        Key capabilities:
        - Get real-time weather data for any location
        - Access air quality information
        - Calculate carbon footprints for activities
        - Generate personalized climate action recommendations
        - Provide seasonal eco-tips

        Always be:
        - Encouraging and positive about climate action
        - Specific and actionable in your recommendations
        - Data-driven and evidence-based
        - Considerate of user constraints (budget, time, difficulty)
        - Focused on both individual and collective impact

        When users ask about climate actions, always consider their local conditions and provide context-specific advice.
        """
        
        self.agent = Agent(
            name="ReGenAI",
            instructions=instructions,
            model=OpenAIChatCompletionsModel(
                model=self.model_name, 
                openai_client=self.client
            ),
            tools=[
                get_weather_data,
                get_air_quality_data,
                calculate_carbon_footprint,
                get_climate_actions,
                get_eco_tips_by_season
            ]
        )
    
    def get_user_id(self):
        """Get or create user ID for memory management"""
        if not self.user_id:
            self.user_id = memory_manager.generate_user_id()
            print(f"🌱 Welcome to ReGenAI! Your user ID: {self.user_id}")
        return self.user_id
    
    async def run_async(self, query: str):
        """Run the agent asynchronously with memory"""
        try:
            # Get user session for memory
            session = memory_manager.create_session(self.get_user_id())
            
            # Run the agent with memory
            result = await Runner.run(
                self.agent,
                query,
                session=session
            )
            
            return result
        except Exception as e:
            print(f"❌ Error running ReGenAI: {str(e)}")
            return None
    
    def run_sync(self, query: str):
        """Run the agent synchronously with memory"""
        try:
            # Get user session for memory
            session = memory_manager.create_session(self.get_user_id())
            
            # Run the agent with memory
            result = Runner.run_sync(
                self.agent,
                query,
                session=session
            )
            
            return result
        except Exception as e:
            print(f"❌ Error running ReGenAI: {str(e)}")
            return None
    
    def get_quick_climate_tips(self):
        """Get quick climate tips for the current season"""
        current_month = datetime.now().month
        tips = get_eco_tips_by_season(current_month)
        return f"🌿 Seasonal Eco-Tips for {datetime.now().strftime('%B')}:\n" + "\n".join(f"• {tip}" for tip in tips)
    
    def calculate_my_footprint(self, activity: str, value: float, unit: str = "kg"):
        """Calculate carbon footprint for user activity"""
        result = calculate_carbon_footprint(activity, value, unit)
        if "error" in result:
            return f"❌ {result['error']}"
        
        return f"""
🌍 Carbon Footprint Analysis:
Activity: {result['activity']} ({result['value']} {result['unit']})
CO2 Emissions: {result['carbon_footprint_kg']} kg
Equivalent to: {result['equivalent_trees']} trees needed to offset
Equivalent to: {result['equivalent_car_km']} km of driving
        """

def main():
    """Main function to run ReGenAI"""
    print("🌱 ReGenAI - AI Climate Action Agent")
    print("=" * 50)
    
    # Initialize ReGenAI
    try:
        regenai = ReGenAI()
        print("✅ ReGenAI initialized successfully!")
        print(f"🤖 Using model: {regenai.model_name}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize ReGenAI: {str(e)}")
        return
    
    # Show quick tips
    print(regenai.get_quick_climate_tips())
    print()
    
    # Interactive loop
    while True:
        try:
            print("💬 Ask me about climate action, weather, carbon footprints, or eco-tips!")
            print("Type 'quit' to exit, 'tips' for seasonal tips, 'footprint' for carbon calculator")
            print("-" * 50)
            
            query = input("🌍 Your question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("🌱 Thank you for using ReGenAI! Keep making a difference! 🌍")
                break
            elif query.lower() == 'tips':
                print(regenai.get_quick_climate_tips())
                continue
            elif query.lower() == 'footprint':
                print("🌍 Carbon Footprint Calculator")
                activity = input("Activity (driving, flying, electricity, etc.): ").strip()
                try:
                    value = float(input("Amount/Value: ").strip())
                    unit = input("Unit (kg, km, kWh, etc.) [default: kg]: ").strip() or "kg"
                    print(regenai.calculate_my_footprint(activity, value, unit))
                except ValueError:
                    print("❌ Please enter a valid number for the value")
                continue
            elif not query:
                continue
            
            # Run the agent
            print("🤔 Analyzing your question...")
            result = regenai.run_sync(query)
            
            if result:
                print("\n🌱 ReGenAI Response:")
                print("=" * 50)
                print(result.final_output)
            else:
                print("❌ Sorry, I couldn't process your request. Please try again.")
            
            print("\n" + "=" * 50)
            
        except KeyboardInterrupt:
            print("\n🌱 Thank you for using ReGenAI! Keep making a difference! 🌍")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main()