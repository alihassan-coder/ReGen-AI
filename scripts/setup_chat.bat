@echo off
REM Chat Dashboard Setup Script for Windows
REM This script sets up the database tables for the chat functionality

echo 🌱 ReGenAI Chat Dashboard Setup
echo ================================
echo.

REM Check if we're in the backend directory
if not exist "main.py" (
    echo ❌ Error: Please run this script from the releafai-backend directory
    exit /b 1
)

echo 📊 Creating database tables...
python scripts\create_chat_tables.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Setup complete!
    echo.
    echo Next steps:
    echo 1. Start the backend: uvicorn main:app --reload
    echo 2. Start the frontend: cd ..\releafai-frountend\regenai-frontend ^&^& npm start
    echo 3. Login and start chatting!
) else (
    echo.
    echo ❌ Setup failed. Please check the error messages above.
    exit /b 1
)

