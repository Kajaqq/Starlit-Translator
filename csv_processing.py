import csv
import pandas as pd

# from overflow_check import load_char_widths

from ai.keys_to_the_castle import origin_row_name,translated_row_name, max_line_length
from tools import merge_dicts

'''
Here we preprocess and postprocess CSV files to a dict
This is very janky, but the overall flow is something like this:
1. Get the file 
2. Check if we want:
 - all the pairs(pass_id=1), 
 - only the non-translated ones(pass_id=2) 
 - or only ones that are longer than the pre-defined length/width(pass_id=3)
3. Assign the correct values to a dict
4. Return the dict.  

As for postprocessing we mostly make sure that the special japanese 
characters in our dict are intact(by using the original keys),then search that key in the csv file, 
and replace the column next to it with the translated version.

 '''

replace_dict = {
    'Kokohaku':'Kohaku',
    'Shiroha':'Kohaku',
    'Kokoro':'Kohaku',
}

def preprocess_csv_to_dict(csv_file_path, pass_nr=1):
    data_dict = {}
    if pass_nr == 3:
        # char_widths = load_char_widths()
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                source = row[origin_row_name]
                translated_str = row[translated_row_name] if translated_row_name in row.keys() else row['target']
                if pass_nr == 1:
                    if translated_str:
                        data_dict[source] = translated_str
                    else:
                        data_dict[source] = ''
                elif pass_nr == 2:
                    if not translated_str:
                        data_dict[source] = ''
                elif pass_nr == 3:
                    line_nr_check, line_len = handle_case_3(translated_str)
                    length_check = [ele >= max_line_length+1 for ele in line_len]
                    if True in length_check or True in line_nr_check:
                        data_dict[source] = translated_str.replace('\n',' ')
    return data_dict

def handle_case_3(text_to_check, char_widths=None):
    lines = text_to_check.splitlines()
    line_nr_check = [len(lines) > 3]
    line_width_list = []
    for line in lines:
        line_width_list.append(len(line))
        # You can use the width based on font width here
        #line_width = 0
        # for char in line:
        #
        #     # char_code = ord(char)
        #     # line_width += char_widths.get(char_code, 0)
        # line_width_list.append(line_width)
    return line_nr_check, line_width_list

def fix_common_mistakes(en_dict: dict, replace_list=None):
    if replace_list is None:
        replace_list = replace_dict
    for replace_key, replace_value in replace_list.items():
        for key, en_text in en_dict.items():
            en_text_words = en_text.split()
            if replace_key in en_text_words:
                en_dict[key] = en_text.replace(replace_key, replace_value)
    return en_dict


def postprocess_dict_to_csv(csv_file_path: str, csv_output_path: str, jp_dict_data: dict, en_dict_data:dict):
    en_dict_data = fix_common_mistakes(en_dict_data)
    dict_data = merge_dicts(jp_dict_data, en_dict_data)
    df = pd.read_csv(csv_file_path)
    dict_data['…………'] = '…………'  # The model doesn't like multiple commas, and we strive for 100% translation
    dict_data['行ってきますっ！'] = "I'm off!"  # The model also doesn't like repeated sentences, and this one is often repeated from different idols
    for jp_text, en_text in dict_data.items():
        mask = df[origin_row_name] == jp_text
        next_column_index = df.columns.get_loc(origin_row_name) + 1
        if next_column_index < len(df.columns):
            next_column_name = df.columns[next_column_index]
            df.loc[mask, next_column_name] = en_text
    df.to_csv(csv_output_path, index=False)