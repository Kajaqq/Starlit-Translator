# Modules
import sys

import csv_processing
import stats
from main import translate_line

untranslated_lines_dict_list = []

"""
This is a module for manual fixing files with some lines lacking translation, 
by translating the empty lines line-by-line instead of batching them.

Shouldn't be needed most of the time but it's here.

It requires a manual input of a list of files to fix.
"""

def create_line_lists(files_list):
    translated_lines_dict_list = []

    # Create a list dicts to translate
    for file in files_list:
        untranslated_lines = csv_processing.preprocess_csv_to_dict(file, pass_nr=2)
        untranslated_lines_dict_list.append(untranslated_lines)

    # Translate the lines
    for dictx in untranslated_lines_dict_list:
        translated_line = translate_line(dictx)
        translated_lines_dict_list.append(translated_line)

    return translated_lines_dict_list


def manual_translate(files_list):
    # Translate the file line-by-line and check the translation state

    translated_dict_list = create_line_lists(files_list)
    for idx, file in enumerate(files_list):
        translation_state1 = stats.check_translation_percentage(file)[file]
        translated_dict = translated_dict_list[idx]
        output = f'{file[:-8]}_fix_eng.csv'
        print('=' * 24)
        print(f"input file: {file}")
        print(f"output file: {output}")
        print(f"dict: {translated_dict}")
        print('=' * 24)
        csv_processing.postprocess_dict_to_csv(file, output, untranslated_lines_dict_list[idx], translated_dict)
        translation_state2 = stats.check_translation_percentage(output)[output]
        print(f"Old percentage: {translation_state1:.2f}%")
        print(f"New percentage: {translation_state2:.2f}%")


if __name__ == '__main__':
    trans_file = 'sample/sample1.csv'
    file_dir = sys.argv[1] if len(sys.argv) > 1 else trans_file
    manual_translate([file_dir])
