#!/bin/bash
# ATM System - Quick Start Script

echo "🏧 ATM Face Recognition System - Quick Start"
echo "=============================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if trainer exists
echo ""
if [ ! -f "trainer/trainer.yml" ]; then
    echo "⚠️  Trained model not found!"
    echo "Do you want to train the model now? (requires dataset/) [y/n]"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo "🔄 Training model..."
        python3 train_model.py
    else
        echo "❌ Cannot proceed without trained model. Run: python3 train_model.py"
        exit 1
    fi
fi

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Run the app
echo ""
echo "🚀 Starting Streamlit app..."
echo "📲 Open your browser to: http://localhost:8501"
echo ""
streamlit run app.py
