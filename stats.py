import csv
import sys

import tools
from ai.keys_to_the_castle import origin_row_name, translated_row_name

def count_translated_str(csv_file_path: str) -> tuple[int, int, int]:
    filled_count = 0
    empty_count = 0
    total = tools.len_csv(csv_file_path)
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            translated_row = row[translated_row_name]
            origin_row = row[origin_row_name]
            if translated_row:
                filled_count += 1
            elif origin_row and not translated_row:
                empty_count += 1
            elif not origin_row and not translated_row:
                filled_count += 1
    return filled_count, empty_count, total


def check_translation_percentage(input_csv):
    results = {}
    file_list = tools.glob_csv_files(input_csv)
    if type(file_list) is str: file_list = [file_list]
    for file_path in file_list:
        filled, empty, total_lines = count_translated_str(file_path)
        total = filled + empty
        if total > 0:  # Avoid division by zero if a file is entirely empty
            percentage = (filled / total) * 100
        else:
            percentage = 0
            print(f"Warning: Total is zero for {file_path}. Cannot calculate percentage.")
        results[file_path] = percentage
        if total != total_lines:
            print(f'Line number mismatch. Something is very wrong.')

    sorted_results = dict(
        sorted(results.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_results


def main(fix_dict):
    trans_sum = 0
    untranslated_list = []
    partly_translated_list = []
    for csv_file, csv_per in fix_dict.items():
        if csv_per == 100:
            trans_sum += 1
        elif 10 < csv_per < 100:
            partly_translated_list.append(f'{csv_file} : {csv_per:.2f}%')
        elif csv_per < 10:
            untranslated_list.append(f'{csv_file} : {csv_per:.2f}%')

    full_percent = (trans_sum / len(fix_dict)) * 100
    print(f'Directory {fix_dir} is {full_percent:.2f}% Translated')
    print(f'Untranslated files')
    if untranslated_list: tools.print_list(untranslated_list)
    print(f'\nPartly translated files')
    if partly_translated_list: tools.print_list(partly_translated_list)


if __name__ == "__main__":
    fix_dir = sys.argv[1] if len(sys.argv) > 1 else 'pevent'
    main(check_translation_percentage(fix_dir))
