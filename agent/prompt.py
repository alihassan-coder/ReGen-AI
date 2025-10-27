"""
ReGenAI Climate Action Prompts
Specialized prompts for different climate action scenarios
"""

# Climate Action Analysis Prompts
CLIMATE_ANALYSIS_PROMPT = """
As ReGenAI, analyze the following environmental data and provide personalized climate action recommendations:

Weather Data: {weather_data}
Air Quality Data: {air_quality_data}
User Location: {location}
Current Season: {season}

Based on this data, provide:
1. Immediate actions (can be taken today)
2. Short-term goals (1-4 weeks)
3. Long-term strategies (1-6 months)
4. Specific environmental impact estimates
5. Cost and difficulty assessments

Focus on actionable, data-driven recommendations that consider local conditions.
"""

# Carbon Footprint Analysis Prompt
CARBON_FOOTPRINT_PROMPT = """
As ReGenAI, analyze this carbon footprint data and provide actionable insights:

Activity: {activity}
Carbon Emissions: {emissions} kg CO2
Equivalent Impact: {equivalent_info}

Provide:
1. Context about the environmental impact
2. Specific ways to reduce this footprint
3. Alternative approaches with lower impact
4. Long-term strategies for similar activities
5. Positive framing to encourage action

Make it personal and motivating while being scientifically accurate.
"""

# Seasonal Climate Tips Prompt
SEASONAL_TIPS_PROMPT = """
As ReGenAI, provide seasonal climate action tips for {month_name}:

Current Month: {month}
Season: {season}
Typical Weather: {weather_patterns}

Provide:
1. 3-5 specific, actionable tips for this season
2. Energy efficiency opportunities
3. Sustainable lifestyle changes
4. Local environmental considerations
5. Preparation for the next season

Make tips practical, achievable, and seasonally relevant.
"""

# Weather-Based Recommendations Prompt
WEATHER_RECOMMENDATIONS_PROMPT = """
As ReGenAI, analyze this weather data and provide climate action recommendations:

Temperature: {temperature}°C
Humidity: {humidity}%
Weather Condition: {description}
Wind Speed: {wind_speed} m/s
Pressure: {pressure} hPa

Based on these conditions, suggest:
1. Energy efficiency opportunities
2. Health and safety considerations
3. Sustainable transportation options
4. Home energy management
5. Outdoor activity recommendations

Consider both immediate comfort and long-term environmental impact.
"""

# Air Quality Action Prompt
AIR_QUALITY_ACTION_PROMPT = """
As ReGenAI, analyze this air quality data and provide health and environmental recommendations:

Air Quality Index: {aqi}
PM2.5: {pm25} μg/m³
PM10: {pm10} μg/m³
Ozone: {o3} μg/m³
Nitrogen Dioxide: {no2} μg/m³

Provide:
1. Health protection measures
2. Indoor air quality improvements
3. Transportation recommendations
4. Long-term air quality improvement strategies
5. Community action suggestions

Balance health protection with environmental responsibility.
"""

# General Climate Education Prompt
CLIMATE_EDUCATION_PROMPT = """
As ReGenAI, explain this climate concept in simple, actionable terms:

Topic: {topic}
User Level: {user_level}
Context: {context}

Provide:
1. Simple, clear explanation
2. Why it matters for climate action
3. How it affects daily life
4. Specific actions the user can take
5. Resources for further learning

Use encouraging, positive language while being scientifically accurate.
"""

# Emergency Climate Response Prompt
EMERGENCY_RESPONSE_PROMPT = """
As ReGenAI, provide immediate climate action guidance for this situation:

Situation: {situation}
Severity: {severity}
Location: {location}
Timeframe: {timeframe}

Provide:
1. Immediate safety measures
2. Environmental protection actions
3. Community response options
4. Long-term resilience building
5. Recovery and adaptation strategies

Prioritize safety while maintaining environmental consciousness.
"""
