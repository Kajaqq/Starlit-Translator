import csv
import glob
import os

import overflow_check
import stats

def len_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        total = sum(1 for _ in reader) - 1
    return total

def dict_to_str(dict_obj: dict):
    # Here we create a string similar to the one in the prompt
    dict_str = ''
    for source, translated in dict_obj.items():
        dict_str += f"source: {source}\ntranslatedstr: {translated}\n---\n"
    return dict_str

def dict_to_list(dict_obj: dict):
    return dict_to_str(dict_obj).strip().split('---')

def get_file_overflow(csv_file):
    overflow_percentage = 0
    char_widths_data = overflow_check.load_char_widths()
    result = overflow_check.analyze_line_widths_from_csv(csv_file, char_widths_data)
    if result['overflow_count']:
        total_lines = result['sum_all']
        overflow_percentage = (result['overflow_count'] / total_lines) * 100 if total_lines > 0 else 0
    return overflow_percentage

def merge_dicts(dict_keys, dict_values):
    dict_keys = dict_keys.keys()
    dict_values = dict_values.values()
    return dict(zip(dict_keys, dict_values))

def print_list(list_obj: list):
    for item in list_obj:
        print(item)

def glob_csv_files(input_csv):
    is_dir = os.path.isdir(input_csv)
    if is_dir:
        pattern = os.path.join(input_csv, "**", "*.csv")
    else:
        return input_csv
    all_csv_files = glob.iglob(pattern, recursive=True)
    return all_csv_files

def glob_and_exclude(directory, exclusion_percentage=100, exclusion_name='_eng.csv'):
    all_csv_files = list(glob_csv_files(directory))
    if not exclusion_percentage and not exclusion_name:
        return all_csv_files
    else:
        exclude_files = set()
        if exclusion_name:
            # Add all files ending with exclusion_name to the set
            exclude_files.update({f for f in all_csv_files if f.endswith(exclusion_name)})
            eng_list = list(exclude_files)
            # Iterate through all files and add the counterpart to exclude_files if it exists
            for f in eng_list:
                exclude_files.add(f.replace(exclusion_name, '.csv'))

        if exclusion_percentage:
            try:
                translation_percentages = stats.check_translation_percentage(directory)
                for csv_file, percentage in translation_percentages.items():
                    if percentage >= exclusion_percentage:
                        exclude_files.add(csv_file)
            except Exception as e:
                print(f"Error checking translation percentages: {e}")

        filtered_files = [f for f in all_csv_files if f not in exclude_files]
        return sorted(filtered_files)
