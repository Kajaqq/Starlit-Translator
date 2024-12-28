import math

from vertexai.preview import tokenization

from tools import dict_to_str, dict_to_list


"""
This file handles the token calculations, 
1.5-pro tokens generally correspond to 2.0 tokens.
"""

def estimate_time(tokens):
    average_tps = 90  # It's hard to give an exact number here as the speed depends on the load of the model,
                      # 2.0-flash-preview can send up to 160t/s but after the roll-out for Gemini Advanced
                      # it slowed down to about 80-90 for a few days to get back to 130 later
                      # therefore this number is the worst-case scenario
    time_in_seconds = int(tokens) / average_tps
    time_in_minutes = time_in_seconds / 60
    estimate = f'a maximum of {time_in_seconds:.2f} second(s), or about {time_in_minutes:.2f} minute(s)'
    return estimate

def count_tokens(text, model="gemini-1.5-pro-002"):
    if type(text) == dict:
        text = dict_to_str(text)
    model_name = model
    tokenizer = tokenization.get_tokenizer_for_model(model_name)
    contents = text
    result = tokenizer.count_tokens(contents)
    total_tokens = result.total_tokens
    return total_tokens


def get_jp_tokens(dict_data: dict):
    dict_list = dict_to_list(dict_data)
    total_tokens = 0
    for line in dict_list:
        total_tokens += count_tokens(line)
    return total_tokens / len(dict_list)


def calculate_chunk_size(dict_data: dict, api_limit=8192):
    """
    Calculates the optimal chunk size (in characters) for API calls.
    We assume that the English translation is 10% more tokens than the JP original(see token_calculations.py)

    Args:
      dict_data: csv_to_dict data to calculate chunk size for
      api_limit: The maximum character limit for an API response(8192 for Gemini).

    Returns:
      The optimal chunk size.

    """

    avg_jp_tokens = get_jp_tokens(dict_data)

    # Calculate the average length of a row *before* the API response

    avg_row_length_before = avg_jp_tokens + 5  # 5 tokens for buffer

    # Calculate the average length of a row *after* the API response
    eng_avg_tokens = avg_jp_tokens * 1.15
    avg_row_length_after = avg_row_length_before + eng_avg_tokens + 5  # 5 tokens for buffer
    print(avg_row_length_after)

    # Estimate the number of rows that can fit in the API response limit
    max_rows_per_response = api_limit / avg_row_length_after

    # Calculate the optimal batch size in characters based on the *input* row length
    optimal_chunk_size = math.floor(max_rows_per_response)

    return avg_jp_tokens, optimal_chunk_size
