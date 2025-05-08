import os
import sys
from time import sleep

from google import genai
from google.genai import types

# Modules
import csv_processing
import stats
import tools
from ai import tokenizer, prompt_gen
from ai.gemini_csv import translate_text
from ai.keys_to_the_castle import api_key, trans_work_dir

# Model settings
client = genai.Client(api_key=api_key)          # import from keys_to_the_castle.py -> generate on the AI Studio site.
model_name = "gemini-2.5-flash-preview-04-17"  # You don't generally want to change this unless you know what you are doing,
generation_config = types.GenerateContentConfig(
    system_instruction=prompt_gen.generate_instructions(),
    # Temperature corresponds to the model 'creativity',
    # For Translation tasks it's best to use a value between 0.00 and 0.30
    temperature=0.15,
    # Setting a seed helps with making the model more predictable
    seed=39,
    # This is the maximum allowed number, we handle this by chunking the lines sent to the model
    # so that the response never surpasses this point.
    response_mime_type='text/plain'
)

model_data = [model_name, generation_config]
def verify_translation(csv_file: str, percentage: int) -> int:
    old_percentage = percentage
    translation_percentage = stats.check_translation_percentage(csv_file)
    new_percentage = translation_percentage[csv_file]
    print(f"Old percentage: {old_percentage:.2f}%")
    print(f"New percentage: {new_percentage:.2f}%")
    if new_percentage == 100:
        print('Translation complete, proceeding.')
    if new_percentage < old_percentage:
        print("Translation has regressed.\nSomething went really wrong.\nRemoving Result.")
    if old_percentage < new_percentage < 100:
        print('Translation partially completed.')
    return new_percentage


def translate_csv(files, pass_nr=1, pass_rate=100):
    files = tools.glob_and_exclude(files) if type(files) is not list else files # Exclude files that are already translated
    for filename in files:
        # Obtain needed data
        file, extension = os.path.splitext(filename)
        file_dict = csv_processing.preprocess_csv_to_dict(filename, pass_nr)
        file_tokens = tokenizer.count_tokens(file_dict, client=client, model=model_name)
        translation_state = stats.check_translation_percentage(filename)[filename] # returns a list so we check the given file.
        file_chunk_size = 100 # This is how many pairs we send to the model at once
        time_estimate = tokenizer.estimate_time(file_tokens)
        ## This is a dynamic chunk size calculator,
        ## not necessarily needed as 100 pairs per chuck is usually good enough.
        # avg_tokens, file_chunk_size = tokenizer.calculate_chunk_size(file_dict)
        # batches_needed = math.ceil(file_tokens / file_chunk_size * avg_tokens)
        print('=' * 32)
        print(f'Starting to process file {filename}, this may take a while, please wait...')
        print(f"File is {translation_state:.2f}% Translated")
        print("Token Count: ", file_tokens)
        print("Chunk Size in pairs: ", file_chunk_size)
        # print("Batches: ", batches_needed)
        print("The first chunk should take about 30 seconds to complete.")
        print(f'Estimated time for the whole file: {time_estimate}', )
        translated_file = translate_text(file_dict, client, model_data, file_chunk_size, file_tokens) # Send the dict and start the translation
        output_path = f'{file}_eng{extension}' if pass_nr == 1 else f'{file[:-4]}_fix_eng{extension}' # Output filename, for explanation about pass_id see csv_processing.py
        csv_processing.postprocess_dict_to_csv(filename, output_path, file_dict, translated_file)
        trans_percent = verify_translation(output_path, translation_state) # Check the state of before and after translation
        if trans_percent < pass_rate and pass_nr == 1: # If the translation is less than pass_rate, then retry one time.
            translate_csv([output_path], pass_nr=2)
        if pass_nr > 1:
            if trans_percent <= translation_state: # If after the second time the translation doesn't improve, remove the new file.
                print('=' * 24)
                print(f"PARTIAL TRANSLATION FIX FAILED FOR {filename}")
                print('=' * 24)
                os.remove(output_path)
                sleep(3)

def translate_line(line):
    file_tokens = tokenizer.count_tokens(line, client=client, model=model_name)
    translated_line = translate_text(line,client, model_data,1, file_tokens)
    return translated_line

if __name__ == '__main__':
    csv_dir = sys.argv[1] if len(sys.argv) > 1 else trans_work_dir
    translate_csv(csv_dir)
