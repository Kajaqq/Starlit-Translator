import csv
import sys
from enum import Enum
from typing import Dict, Optional

import tools
from ai.keys_to_the_castle import trans_work_dir

"""
This file characters width from a csv generated from font_tool.py, and checks the width of the string from csv. 
Credits for this approach go to @faraplay at the IM@S Translation Discord
I've only rewritten their Sheets formula to a python script for this project.
"""

class OVERFLOW_THRESHOLDS(Enum):
    CRITICAL = 50
    RED = 27.959
    YELLOW = 27.6

def load_char_widths(charwidths_csv: str = "charwidths2.csv") -> Optional[Dict[int, float]]:
    """
    Loads character widths from the specified CSV file.
    """
    char_widths: Dict[int, float] = {}
    try:
        with open(charwidths_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    char_code = int(row['CharCode'])
                    width = float(row['Width'])
                    char_widths[char_code] = width
                except (ValueError, KeyError, TypeError):
                    print(f"Skipping invalid row or missing data in charwidths: {row}")
        return char_widths
    except FileNotFoundError:
        print(f"Error: charwidths file not found at {charwidths_csv}")
        return None

def analyze_line_widths_from_csv(csv_file: str, char_widths: Dict[int, float]) -> Optional[Dict[str, int]]:
    """
    Analyzes line widths in a CSV file based on character widths.
    """

    critical_count = 0
    red_count = 0
    yellow_count = 0
    green_count = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                text = row['translatedstr'] if 'translatedstr' in row.keys() else row['target']
                lines = text.splitlines()

                for line in lines:
                    line_width = 0
                    for char in line:
                        char_code = ord(char)
                        line_width += char_widths.get(char_code,0)

                    if line_width > OVERFLOW_THRESHOLDS.CRITICAL.value:
                        critical_count += 1
                    elif line_width >= OVERFLOW_THRESHOLDS.RED.value:
                        red_count += 1
                    elif OVERFLOW_THRESHOLDS.YELLOW.value <= line_width >= OVERFLOW_THRESHOLDS.RED.value:
                        yellow_count += 1
                    else:
                        green_count += 1


        return {
            "filename": csv_file,
            'critical_count': critical_count,
            "red_count": red_count,
            "yellow_count": yellow_count,
            "green_count": green_count,
            'overflow_count': red_count + yellow_count,
            'sum_all': yellow_count + green_count + red_count,

        }
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file}")
        return None


def check_widths(csv_files):
    char_widths_data = load_char_widths()
    csv_list = tools.glob_csv_files(csv_files)
    width_list = []  # Store results in a list
    for file in csv_list:
        res = analyze_line_widths_from_csv(file, char_widths_data)
        if res:
            width_list.append(res)
    width_list = sorted(width_list, key=lambda item: item['overflow_count'], reverse=True)
    return width_list

def check_line_width(lines):
    char_widths = load_char_widths()
    line_width_list = []
    lines = lines.splitlines()
    for line in lines:
        line_width = 0
        for char in line:
            char_code = ord(char)
            line_width += char_widths.get(char_code, 0)
        line_width_list.append(line_width)
    return line_width_list

if __name__ == "__main__":
    check_dir = sys.argv[1] if len(sys.argv) > 1 else trans_work_dir
    width_list = check_widths(check_dir)
    sum_all = 0
    overflow_all = 0
    for result in width_list:
        sum_all += result['sum_all']
        if result:
            overflow_all += result['overflow_count']
            total_lines = result['sum_all']
            overflow_percentage = (result['overflow_count'] / total_lines) * 100 if total_lines > 0 else 0
            # print(f"{result['filename']} : {overflow_percentage:.2f}%")
            print('=' * 24)
            print(f'File: {result["filename"]}')
            print(f'Critical count: {result["critical_count"]}')
            print(f"Red count: {result['red_count']}")
            print(f"Yellow count: {result['yellow_count']}")
            print(f"Overflow possible in: {overflow_percentage:.2f}% lines")
    overflow_overall_percent = (overflow_all / sum_all) * 100 if sum_all > 0 else 0
    print('=' * 48)
    print('OVERALL STATISTICS:')
    print(f'{overflow_all} lines have overflow out of {sum_all} lines.\nThat turns out to about {overflow_overall_percent:.2f}% of all lines.')

