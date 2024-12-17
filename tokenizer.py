import csv
import glob
import math
from vertexai.preview import tokenization

def estimate_time(tokens):
    average_tps = 131.67 # No official figure released by google, taken from own experience for gemini-2.0-flash model
    time_in_seconds = math.floor(int(tokens)/average_tps)
    time_in_minutes = math.floor(time_in_seconds/60)
    estimate = f'{time_in_seconds} second(s), or about {time_in_minutes} minute(s)'
    return estimate

def count_tokens(text, model="gemini-1.5-pro-002"):
    model_name = model
    tokenizer = tokenization.get_tokenizer_for_model(model_name)
    contents = text
    result = tokenizer.count_tokens(contents)
    total_tokens = result.total_tokens
    return total_tokens

def get_jp_tokens(csv_data):
    tokens = 0
    n=0
    with open(csv_data, 'r', encoding='utf-8') as f:
        csv_file = csv.reader(f)
        for line in csv_file:
            t = line[2]
            n +=1
            tokens += count_tokens(t)
        average_tokens = tokens / n
        return average_tokens

def calculate_chunk_size(csv_file, col1_tokens=8, col2_tokens=2, api_limit=8192):
    """
    Calculates the optimal chunk size (in characters) for API calls.
    We assume that the English translation is 10% more tokens than the JP original(see token_calculations.py)

    Args:
      csv_file: csv file to calculate chunk size for
      col1_tokens: The average number of tokens of the first column.(about 8 for IM@S)
      col2_tokens: The maximum number of tokens of the second column.(about 2 for IM@S)
      api_limit: The maximum character limit for an API response(8192 for Gemini).

    Returns:
      The optimal chunk size.

    """
    # The average number of tokens of the third column.(about 15 for IM@S, but dynamically calculated cause why not)
    jp_avg_tokens = get_jp_tokens(csv_file)
    # Calculate the average length of a row *before* the API response
    avg_row_length_before = col1_tokens + col2_tokens + jp_avg_tokens + 2  # 2 tokens for buffer

    # Calculate the average length of a row *after* the API response
    eng_avg_tokens = jp_avg_tokens * 1.1
    avg_row_length_after = avg_row_length_before + eng_avg_tokens

    # Estimate the number of rows that can fit in the API response limit
    max_rows_per_response = api_limit / avg_row_length_after

    # Calculate the optimal batch size in characters based on the *input* row length
    optimal_chunk_size = math.floor(max_rows_per_response * avg_row_length_before)

    return optimal_chunk_size

def token_stats(data):
    """
    Gives some useless token statistics about given folder with csv files

    Args:
        data: The folder containing csv files

    Returns:
      jp_tokens: the average number of tokens/per line of the JP text
      full_tokens: the number of tokens of the whole file
      average_tokens: the average number of tokens of all files
      a
    """
    token_sum = 0
    file_number = 0
    full_token_sum = 0
    for filename in glob.iglob(data):
        with open(filename, 'r', encoding='utf-8') as f:
            file_ = f.read()
            jp_tokens = get_jp_tokens(filename)
            token_sum += jp_tokens
            file_number += 1
            file_tokens = count_tokens(file_)
            full_token_sum += file_tokens
            print(filename, " JP Token Count: ", jp_tokens)
            print(filename, " Full Token Count: ", file_tokens)
    average_tokens = math.floor(token_sum / file_number)
    average_jp_tokens = math.floor(jp_tokens / file_number)
    print("Average JP Token/Line Count: ", average_jp_tokens)
    print("Average Token Count: ", average_tokens)