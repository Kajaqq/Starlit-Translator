import os
import sys

import google.generativeai as genai
import csv_processing
import overflow_check
import prompt_gen
import tokenizer
import tools
from gemini_csv import translate_text
from keys_to_the_castle import api_key
from tools import get_file_overflow

"""
This is a special version of main.py dedicated to minimizing the problem of text overflowing.
The optimal method I found is 3 passes per file. 
It can minimize the overflow from 25% down to even 2% by line-breaking and rewording.
The downsize is that models have problems with counting sometimes, and instead of 2 reworded lines, we get 3.
But that can be easily detected and fixed in human proofread.
"""


# Model settings
genai.configure(api_key=api_key)     # import from keys_to_the_castle.py -> generate on the AI Studio site.
model_name = "gemini-2.0-flash-exp"  # You don't generally want to change this except if you know what you are doing,
                                     # 2.0-flash-thinking generally performs worse

generation_config = {
    # Temperature corresponds the model 'creativity',
    # For Translation tasks it's best to use a value between 0.00 and 0.30
    "temperature": 0.15,
    # This is the maximum allowed number, we handle this by chunking the lines sent to the model
    # so that the response never surpasses that point.
    "max_output_tokens": 8192,
    # Other possible option is 'text/json', but that would require a rewrite
    # of parsing the output from the model.
    "response_mime_type": "text/plain",
}


model = genai.GenerativeModel(
    model_name=model_name,
    generation_config=generation_config,
    system_instruction=prompt_gen.generate_instructions()
)


def check_width_line(lines):
    char_widths = overflow_check.load_char_widths()
    line_width_list = []
    lines_split = []
    for line in lines:
        lines_split.append(line.splitlines())
    for line_split in lines_split:
        line_width = 0
        for char in line_split:
            char_code = ord(char)
            line_width += char_widths.get(char_code, 0)
        line_width_list.append(line_width)
    return line_width_list

def process_csv(files, pass_id=3, passes=3):
    files = tools.glob_and_exclude(files, None, None) if type(files) is not list else files
    for filename in files:
        for p in range(1, passes+1):
            file, extension = os.path.splitext(filename)
            file_dict = csv_processing.preprocess_csv_to_dict(filename, pass_id)
            file_tokens = tokenizer.count_tokens(file_dict)
            overflow_state = get_file_overflow(filename)
            file_chunk_size = 100
            time_estimate = tokenizer.estimate_time(file_tokens)
            print('=' * 32)
            print(f'Starting to process file {filename}, this may take a while, please wait...')
            print(f'Pass nr: {p}/{passes}')
            print(f"File overflow state: {overflow_state:.2f}%")
            print("Token Count: ", file_tokens)
            print("Chunk Size in Lines: ", file_chunk_size)
            print("The first chunk should take about 30-40 seconds to complete.")
            print(f'Estimated time for the whole file: {time_estimate}')
            translated_file = translate_text(file_dict, model, file_chunk_size, file_tokens)
            output_path = f'{file}_fix{p}{extension}' if p ==1 else f'{file[:-1]}{p}{extension}'
            csv_processing.postprocess_dict_to_csv(filename, output_path, file_dict, translated_file)
            overflow_state_after = get_file_overflow(output_path)
            if overflow_state_after >= overflow_state:
                os.remove(output_path)
            else:
                filename = output_path
            print(f"File overflow state after: {overflow_state_after:.2f}%")


if __name__ == '__main__':
    fix_dir = sys.argv[1] if len(sys.argv) > 1 else 'sample'
    process_csv(fix_dir)