from flask import Flask, render_template, request, jsonify
import json
from llm import api_call
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_input = data.get("prompt")
    if not user_input:
        return jsonify({"reply": "Invalid input."})
    
    response = api_call(user_input)
    response_json = json.loads(response)  # Parse the JSON string
    return jsonify(response_json)

if __name__ == '__main__':
    app.run(debug=True)