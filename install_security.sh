#!/bin/bash

# Install security dependencies
echo "🔒 Installing security dependencies..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install new security-related packages
pip install Flask-Limiter==3.5.0
pip install PyJWT==2.8.0
pip install python-dotenv==1.0.0

echo "✅ Security dependencies installed successfully!"
echo ""
echo "New features added:"
echo "🔒 Rate Limiting - 5 attempts per minute for login, 100 requests per hour globally"
echo "📝 Security Logging - JSON-formatted logs with request context"
echo "🎫 JWT Tokens - Stateless authentication with 1-hour expiration"
echo ""
echo "To test the new features:"
echo "1. Start the application: python app.py"
echo "2. Login to get a JWT token: POST /login"
echo "3. Use the token for protected routes: Authorization: Bearer <token>"
echo "4. Check security.log for detailed security events"
