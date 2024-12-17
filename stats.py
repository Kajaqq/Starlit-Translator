import csv
import glob
import matplotlib.pyplot as plt


def count_translated_str(csv_file_path):
    filled_count = 0
    empty_count = 0

    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['translatedstr']:  # Check if 'translatedstr' is not empty
                filled_count += 1
            else:
                empty_count += 1

    return filled_count, empty_count

def analyze_multiple_files(file_pattern):
    """
    Analyzes multiple CSV files, calculates percentages of filled 'translatedstr', and visualizes them.

    Args:
        file_pattern (str): A pattern to match CSV files (e.g., '*.csv').
    """
    results = []
    for file_path in glob.glob(file_pattern):
        filled, empty = count_translated_str(file_path)
        total = filled + empty
        if total > 0:  # Avoid division by zero if a file is entirely empty
            percentage = (filled / total) * 100
        else:
            percentage = 0  # Or handle it as you see fit
        results.append((file_path, percentage))

    # Sorting for clearer visualization (optional)
    results.sort(key=lambda x: x[1])  # Sort by percentage

    # Visualization
    file_names, percentages = zip(*results)
    plt.figure(figsize=(10, 6))  # Adjust figure size as needed
    plt.bar(file_names, percentages)
    plt.xlabel("File Names")
    plt.ylabel("Percentage of Filled 'translatedstr'")
    plt.title("Comparison of 'translatedstr' Completion Rates")
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
    plt.tight_layout()
    plt.show()


# Example usage (replace with your file pattern)
analyze_multiple_files('Idol/*.csv')
