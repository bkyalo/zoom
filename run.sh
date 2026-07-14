#!/bin/bash

# Set script to exit immediately if a command exits with a non-zero status
set -e

# Use the caller's current working directory (do not cd to the script path)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Zoom License Manager...${NC}"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "❌ ${YELLOW}Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}🔄 Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate 2>/dev/null || {
        echo -e "❌ ${YELLOW}Failed to activate virtual environment${NC}"
        exit 1
    }
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo -e "${GREEN}✅ Using existing virtual environment${NC}"
    source venv/bin/activate 2>/dev/null || {
        echo -e "❌ ${YELLOW}Failed to activate virtual environment${NC}"
        exit 1
    }
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}ℹ️  Please edit the .env file with your configuration and run this script again.${NC}"
        exit 1
    else
        echo -e "❌ ${YELLOW}.env.example file not found. Please create it first.${NC}"
        exit 1
    fi
fi

# Run the application
echo -e "\n${GREEN}🚀 Starting license management...${NC}"
python app.py

echo -e "\n${GREEN}✅ Script completed successfully!${NC}"
