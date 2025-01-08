﻿# Starlit Translator

This is a project for translating csv files to English with the help of Gemini-2.0-flash or other Google models.

The use case shown here is translating a Japanese game that has never been localized outside Asia.

<p align="center">
    <img src="https://project-imas.wiki/images/d/d5/StarlitSeasonLogo.png"  alt="Starlit Season logo"/>
</p>

## Quick Start
1. Rename keys_to_the_castle.example to keys_to_the_castle.py and enter your [Google AI Studio API key](https://aistudio.google.com/apikey)
2. Install dependencies with 
```bash
   pip install -r requirements.txt
```
3. Run main.py, it will start translating the sample files.


## Project files
The project files can be split into two groups.
#### AI Model tools:
    gemini_csv.py - The heart of the translator, contains the prompt, main logic of translating and chunking and return translated text.
    prompt_gen.py - Contains the system instructions for the model and returns them in a json format
    token_calculations.py - Allows to check chars/token for Japanese and English.
    tokenizer.py - Returns tokens for given text, estimates the time until completion.
    main.py - Utilizing all the above translates a given csv file, checks it's translation rate and saves it back.
    gemini_line_fixer.py - Using line_check.py, tries to fix text overflow by specifically prompting the model with long lines.
    manual_fix.py - Allows for simple line-by-line translations on files with missing translations. 
    keys_to_the_castle.py - Contains the API key for Google AI Platform
    
#### Pre- / post-processing tools:
    stats.py - Provides the translation rate of a given file/files.
    csv_processing.py - Converts the csv into a {key:value} dict, then saves a translated one back to csv.
    line_check.py - Checks the width of a line using the game font width data, returns possible text overflow rate.
    tools.py - Contains common functions to avoid repeating them in code.
    rename.ps1 - A Powershell script to replace old files with translated ones.


## Customization 
You can easily customize this project to your own needs by editing the prompt_gen.py file and entering your own instructions for the model.

Bear in mind that if you do not enter your own instructions the model ***WILL*** perform badly.

Other places for customization are gemini_csv.py and the prompt, csv_processing.py and the CSV Columns, and tools.py for editing the common functions.
