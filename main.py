import csv
import math
import os

import prompt_gen
from gemini_csv import translate_text
from keys_to_the_castle import api_key
import glob
import google.generativeai as genai
from tokenizer import count_tokens, calculate_chunk_size, estimate_time
from os.path import splitext

# Model settings
genai.configure(api_key=api_key) # import from keys_to_the_castle.py -> generate on the AI Studio site.
generation_config = {
    "temperature": 0.15,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
# noinspection PyTypeChecker
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # Don't change this if you don't need to
    generation_config=generation_config,
    #system_instruction="You are a highly skilled professional Japanese-English and English-Japanese translator. Translate the given text accurately, taking into account the context and specific instructions provided. Steps may include hints enclosed in square brackets [] with the key and value separated by a colon:. Only when the subject is specified in the Japanese sentence, the subject will be added when translating into English. If no additional instructions or context are provided, use your expertise to consider what the most appropriate context is and provide a natural translation that aligns with that context. When translating, strive to faithfully reflect the meaning and tone of the original text, pay attention to cultural nuances and differences in language usage, and ensure that the translation is grammatically correct and easy to read. After completing the translation, review it once more to check for errors or unnatural expressions. For technical terms and proper nouns, either leave them in the original language or use appropriate translations as necessary. Take a deep breath, calm down, and start translating",
    system_instruction=prompt_gen.create_prompt()
)

def load_csv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def glob_csv_files(directory):
    pattern = os.path.join(directory, "**", "*.csv")
    all_csv_files = glob.glob(pattern, recursive=True)
    exclude_files = {
        f
        for f in all_csv_files
        if f.endswith("_eng.csv") or f.replace(".csv", "_eng.csv") in all_csv_files
    }
    return [f for f in all_csv_files if f not in exclude_files]


for filename in glob_csv_files("Localize"):
    file, extension = splitext(filename)
    file_content = load_csv(filename)
    file_tokens = count_tokens(file_content)
    file_chunk_size = calculate_chunk_size(filename)
    batches_needed = math.ceil(file_tokens / file_chunk_size)
    time_estimate = estimate_time(file_tokens)
    print('='*32)
    print(f'Starting to process file {filename}, this may take a while, please wait...')
    print("Token Count: ", file_tokens)
    # print("Chunk Size: ", file_chunk_size)
    print("Batches: ", batches_needed)
    print("The first batch should take about 30 seconds to complete.")
    print(f'Estimated time for the whole file: {time_estimate}', )
    translated_file = translate_text(file_content, model, file_chunk_size)
    with open(f"{file}_eng{extension}", "w", encoding="utf-8") as outfile:
        outfile.write(translated_file)
