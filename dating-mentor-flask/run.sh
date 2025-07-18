#!/bin/bash

# Dating Mentor AI - Run Script

echo "🚀 Starting Dating Mentor AI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download NLTK data if needed
echo "📊 Checking NLTK data..."
python -c "import nltk; nltk.download('vader_lexicon', quiet=True)"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found! Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your API keys"
fi

# Create uploads directory if it doesn't exist
mkdir -p static/uploads

# Run the application
echo "✨ Starting Flask application..."
echo "🌐 Open http://localhost:5000 in your browser"
echo "📌 Press Ctrl+C to stop the server"
echo ""

python app.py
