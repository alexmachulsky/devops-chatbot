from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Ollama configuration
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://ollama:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')

# System prompt for general AI assistant
SYSTEM_PROMPT = """You are a knowledgeable and helpful AI assistant. You can discuss any topic including:
- Technology, programming, and software development
- Science, mathematics, and engineering
- Business, finance, and economics
- Arts, literature, and culture
- History, geography, and current events
- Health, fitness, and wellness
- And much more

Provide clear, accurate, and helpful responses. Use examples when appropriate.
Be conversational and friendly. If you're not sure about something, say so."""

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        conversation_history = data.get('history', [])
        
        # Build conversation context for Ollama
        context = SYSTEM_PROMPT + "\n\n"
        
        # Add conversation history
        for msg in conversation_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n\n"
        
        # Add current user message
        context += f"User: {user_message}\n\nAssistant:"
        
        # Call Ollama API
        ollama_response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": context,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            },
            timeout=60
        )
        
        if ollama_response.status_code != 200:
            raise Exception(f"Ollama API error: {ollama_response.text}")
        
        assistant_message = ollama_response.json()["response"]
        
        return jsonify({
            'message': assistant_message.strip(),
            'success': True
        })
    
    except requests.exceptions.Timeout:
        app.logger.error("Ollama request timed out")
        return jsonify({
            'error': 'Request timed out. The model might be loading. Please try again.',
            'success': False
        }), 504
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred processing your request',
            'success': False
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'devops-chatbot'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
