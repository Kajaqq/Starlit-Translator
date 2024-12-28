import csv

import tools


def count_translated_str(csv_file_path):
    filled_count = 0
    empty_count = 0
    total = tools.len_csv(csv_file_path)
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            translated_row = row['translatedstr'] if 'translatedstr' in row else row['target']
            if translated_row:
                filled_count += 1
            else:
                empty_count += 1

    return filled_count, empty_count, total


def check_translation_percentage(input_csv, exclusion_percentage=None, exclusion_name=None):
    results = {}
    file_list = tools.glob_and_exclude(input_csv, exclusion_percentage, exclusion_name)
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


if __name__ == "__main__":
    fix_list = check_translation_percentage('pakchunk99-EngPatch/Commu')
    for csv_file, csv_per in fix_list.items():
        print(csv_file + '\n' + str(csv_per))
