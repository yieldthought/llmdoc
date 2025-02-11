from flask import Flask, render_template, request, jsonify
import requests
import os
import json
from openai import OpenAI

app = Flask(__name__)

# Ensure the API key is set in the environment variables
def api_call(prompt):
    try:
        client = OpenAI(
            api_key=os.environ.get("API_KEY"),
            base_url="https://vllm--tenstorrent.workload.tenstorrent.com/v1",
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="tenstorrent/Meta-Llama-3.1-70B-Instruct",
            max_tokens=128,
        )
        return chat_completion.to_json(indent=4)
    except Exception as e:
        print(f"Error: {e}")
        return json.dumps({"error": str(e)})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_input = data.get("prompt")
    print(f"Miguel: user input = {user_input}")
    if not user_input:
        return jsonify({"reply": "Invalid input."})
    
    response = api_call(user_input)
    print(f"Miguel: Response = {response}")
    response_json = json.loads(response)  # Parse the JSON string
    print(f"Miguel: JSON Response = {response}")
    return jsonify(response_json)

if __name__ == '__main__':
    app.run(debug=True)