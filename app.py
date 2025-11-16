from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# System prompt for DevOps assistant
SYSTEM_PROMPT = """You are a helpful DevOps assistant specializing in:
- Docker and containerization
- Kubernetes orchestration
- CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI)
- Infrastructure as Code (Terraform, Ansible)
- Cloud platforms (AWS, Azure, GCP)
- Monitoring and logging (Prometheus, Grafana, ELK/EFK stack)
- Linux system administration
- Git and version control
- Security best practices

Provide clear, practical advice with code examples when appropriate. 
Be concise but thorough. If you're not sure about something, say so."""

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message']
        conversation_history = data.get('history', [])
        
        # Build messages array with system prompt and conversation history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        assistant_message = response.choices[0].message.content
        
        return jsonify({
            'message': assistant_message,
            'success': True
        })
    
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
