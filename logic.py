from data import search_repo
from llm import api_call

def get_search_terms(question):
    """
    Extract some good search terms from the user's question
    """
    prompt = f"""
    To answer the user's question we are first going extract good search terms. These terms will be grepped for in a large codebase, so they must be specific and literal.
    Return each search term on a new line with no other text. Do not create lots of redundant terms, be specific and do not invent things the user did not mention.
    If there is only one obvious term, just use that one term.

    User's question: {question}
    """
    answer = api_call(prompt)
    return [answer.strip() for answer in answer.split('\n') if answer.strip()]


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

def answer_question(question):
    """
    Answer a question using the tt-metal repo
    """
    search_terms = get_search_terms(question)
    search_results = get_search_results(search_terms)
    return get_answer(question, search_results)