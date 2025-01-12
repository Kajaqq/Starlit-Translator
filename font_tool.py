import csv
import sys

from fontTools.ttLib import TTFont

"""
This file creates a charwidths.csv file from your given ttf font.
Use it if you want to check the width of a line later with overflow_check.py
"""

def get_advance_widths_unicode(font_path):
    """
    Gets the advance widths for each glyph in a font file, represented as a list of dictionaries.

    Args:
        font_path (str): The path to the font file.

    Returns:
        list: A list of dictionaries, where each dictionary has a 'charCode' (decimal Unicode)
              and 'width' (advance width).
    """
    try:
        font = TTFont(font_path)
        hmtx = font['hmtx']
        cmap = font['cmap'].getBestCmap()
        advance_widths_list = []

        for char_code, glyph_name in cmap.items():
            if glyph_name in hmtx.metrics:
                advance_widths_list.append({
                    'CharCode': char_code,
                    'Width': hmtx[glyph_name][0]/1000
                })

        font.close()
        return advance_widths_list

    except Exception as e:
        print(f"Error processing font file: {e}")
        return None

header_fields = ['CharCode','Width']
font_file = sys.argv[1] if len(sys.argv) > 1 else 'Fonty8.ttf'
advance_widths_data = get_advance_widths_unicode(font_file)

if advance_widths_data:
    with open("charwidths.csv", "w", newline="") as f:
        w = csv.DictWriter(f, header_fields)
        w.writeheader()
        w.writerows(advance_widths_data)