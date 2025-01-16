import os
import sys

import csv_processing
import tools
from ai.keys_to_the_castle import trans_work_dir

"""
This is a csv line splitter made to check the overflow state of a file, 
and if the file has any, it splits the line after a given amount of characters.
"""

def split_csv_lines(files, pass_id=3):
    files = tools.glob_and_exclude(files, None, None) if type(files) is not list else files
    for filename in files:
        file, extension = os.path.splitext(filename)
        overflow_state = tools.get_file_overflow(filename)
        if overflow_state == 0:
            continue
        file_dict = csv_processing.preprocess_csv_to_dict(filename, pass_id)
        print('=' * 32)
        print(f'Processing: {filename}')
        print(f"File overflow state: {overflow_state:.2f}%")
        translated_file = tools.split_dict(file_dict)
        output_path = f'{file}_fix{extension}'
        csv_processing.postprocess_dict_to_csv(filename, output_path, file_dict, translated_file)
        overflow_state_after = tools.get_file_overflow(output_path)
        if overflow_state_after >= overflow_state:
            os.remove(output_path)
        print(f"File overflow state after: {overflow_state_after:.2f}%")


if __name__ == '__main__':
    fix_dir = sys.argv[1] if len(sys.argv) > 1 else trans_work_dir
    split_csv_lines(fix_dir)