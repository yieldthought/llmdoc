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
    
    try:
        response = answer_question(user_input)
        # Add type checking and convert to string if needed
        if not isinstance(response, str):
            response = str(response)
        
        # Add debug print
        print(f"Response type: {type(response)}, Value: {response}")
        
        return jsonify({"reply": response})
    except Exception as e:
        print(f"Error during jsonify: {str(e)}")
        return jsonify({"reply": "An error occurred.", "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)