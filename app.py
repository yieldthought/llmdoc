from flask import Flask, render_template, request, jsonify
import json
from logic import answer_question
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
    
    response = answer_question(user_input)    
    return jsonify({"reply": response})

if __name__ == '__main__':
    app.run(debug=True)