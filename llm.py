from openai import OpenAI
import os
import json

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

