#!/bin/bash

# Chat Dashboard Setup Script
# This script sets up the database tables for the chat functionality

echo "🌱 ReGenAI Chat Dashboard Setup"
echo "================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the releafai-backend directory"
    exit 1
fi

echo "📊 Creating database tables..."
python scripts/create_chat_tables.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Start the backend: uvicorn main:app --reload"
    echo "2. Start the frontend: cd ../releafai-frountend/regenai-frontend && npm start"
    echo "3. Login and start chatting!"
else
    echo ""
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi

