from data import update_tt_metal_repo, search_repo
from openai import OpenAI


def get_search_terms(question):
    """
    Extract some good search terms from the user's question
    """
    # FIXME: use an LLM
    return question.split()

def get_search_results(search_terms):
    """
    Search the tt-metal repo for the search terms
    """
    all_results = []
    for search_term in search_terms:
        results = search_repo(search_term)
        all_results.extend(results)
    return all_results

def get_answer(question, search_results):
    """
    Use an LLM to answer the question based on the search results
    """
    client = OpenAI()
    
    # Prepare context from search results
    context = "\n\n".join(search_results)
    
    # Construct the prompt
    prompt = f"""Given the following context from a technical documentation:

{context}

Please answer this question in detail, providing 2-3 examples where applicable:
{question}"""

    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful technical assistant that provides detailed answers with examples."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

