import csv
import glob
import operator
import os

import line_check
import stats


def len_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        total = sum(1 for row in reader) - 1
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
    char_widths_data = line_check.load_char_widths()
    result = line_check.analyze_line_widths_from_csv(csv_file, char_widths_data)
    if result['overflow_count']:
        total_lines = result['sum_all']
        overflow_percentage = (result['overflow_count'] / total_lines) * 100 if total_lines > 0 else 0
    return overflow_percentage

def merge_dicts(dict_keys, dict_values):
    return dict(zip(dict_keys, dict_values))


def glob_csv_files(input_csv):
    is_dir = True if os.path.isdir(input_csv) else False
    if is_dir:
        pattern = os.path.join(input_csv, "**", "*.csv")
    else:
        return input_csv
    all_csv_files = glob.iglob(pattern, recursive=True)
    return all_csv_files


def glob_and_exclude(directory, exclusion_percentage=100, exclusion_name='_eng.csv', op=operator.eq):
    all_csv_files = glob_csv_files(directory)

    if exclusion_percentage or exclusion_name:
        exclude_files = set()

        if exclusion_name:
            exclude_files = {f for f in all_csv_files if f.endswith(exclusion_name)}
            for f in all_csv_files:
                if not f.endswith(exclusion_name):
                    eng_counterpart = f[:-4] + exclusion_name
                    if eng_counterpart in all_csv_files:
                        exclude_files.add(f)

        if exclusion_percentage:
            try:
                translation_percentages = stats.check_translation_percentage(directory)
                for csv_file, percentage in translation_percentages.items():
                    if op(percentage, exclusion_percentage):
                        exclude_files.add(csv_file)
            except Exception as e:
                print(f"Error checking translation percentages: {e}")

        filtered_files = [f for f in all_csv_files if f not in exclude_files]
        return sorted(filtered_files)

    else:
        return all_csv_files
