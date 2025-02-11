from data import search_repo, get_more_context
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


def select_best_results(question, search_results):
    """
    Use an LLM to select the best results from the search results
    """
    search_results_str = "\n\n".join([f"SEARCH RESULT {i+1}:\n{result}\n\n" for i, result in enumerate(search_results)])
    prompt = f"""
    Given the following search results, select a few that you want to see in full detail to answer the question.

    Search results:
    {search_results_str}

    Question: {question}

    Return the search results in a list of indices, separated by commas.
    Example: "2, 1, 5"

    Return only the list of indices, no other text.
    """
    answer = api_call(prompt)
    return [ search_results[int(index)-1] for index in answer.split(',') ]


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
    print(f'Question: {question}')

    search_terms = get_search_terms(question)
    print(f'Search terms: {search_terms}')

    search_results = get_search_results(search_terms)
    print(f'Search results: {len(search_results)}')
    print(f'Files: {[result["file"] for result in search_results]}')

    # best_results = select_best_results(question, search_results)
    # print(f'Best results: {len(best_results)}')

    # extended_results = [ get_more_context(search_terms, result) for result in best_results ]
    # print(f'Extended results: {len(extended_results)}')

    answer = get_answer(question, search_results)
    print(f'Answer: {answer}')

    return answer
