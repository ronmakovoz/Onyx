#!/bin/bash
set -e

echo "==> Installing dependencies..."
pip install -r requirements.txt -q

echo "==> Seeding database..."
python data/synthetic_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the app:"
echo "  Terminal 1: uvicorn backend.main:app --reload --port 8000"
echo "  Terminal 2: streamlit run frontend/app.py"
echo ""
echo "Optional: Set ANTHROPIC_API_KEY for live Claude responses."
echo "  export ANTHROPIC_API_KEY=your_key_here"
echo ""
echo "Mock mode is active by default (no API key required)."
