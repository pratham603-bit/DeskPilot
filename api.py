from flask import Flask, request, jsonify, render_template
from agent import chat

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' in request body."}), 400
        
    message = data['message']
    history = data.get('history', [])
    
    try:
        response = chat(message, history)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
