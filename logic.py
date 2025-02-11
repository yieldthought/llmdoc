from data import update_tt_metal_repo, search_repo
from llm import api_call


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
    prompt = f"""
    Given the following search results, answer the question:
    {search_results}
    Question: {question}
    """
    return api_call(prompt)

