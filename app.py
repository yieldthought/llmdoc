from flask import Flask, render_template, request, jsonify
import requests

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
    
    # Replace this with actual API call to an LLM
    response = {"reply": f"AI Response to: {user_input}"}  
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
