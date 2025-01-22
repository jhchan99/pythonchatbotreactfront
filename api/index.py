from http.server import BaseHTTPRequestHandler
from .SwornOfficerChatbot import ContentChatbot
import json

chatbot = ContentChatbot()

def handle_chat(request_body):
    try:
        user_input = request_body.get('message')
        if not user_input:
            return {'error': 'No message provided'}, 400
        
        response = chatbot.chat(user_input)
        return {'response': response}, 200
    except Exception as e:
        return {'error': str(e)}, 500

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Only handle /api/chat endpoint
        if self.path != '/api/chat':
            self.send_response(404)
            self.end_headers()
            return

        # Read the request body
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length)
        request_json = json.loads(request_body)

        # Process the chat request
        response_data, status_code = handle_chat(request_json)

        # Send response
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json.dumps(response_data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Add to your index.py, at the bottom
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/api/chat', methods=['POST', 'OPTIONS'])
    def chat_endpoint():
        if request.method == 'OPTIONS':
            return '', 200
            
        # Use your existing handle_chat function
        response_data, status_code = handle_chat(request.json)
        return jsonify(response_data), status_code

    print("Starting development server on port 8000...")
    app.run(port=8000, debug=True)