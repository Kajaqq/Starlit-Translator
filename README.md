# Starlit Translator

This is a PoC module pack for translating csv files with the help of Gemini-2.0-flash or other Google models.

The usecase shown here is translating a Japanese game that has never been localized outside Asia.

<p align="center">
<img src="https://project-imas.wiki/images/d/d5/StarlitSeasonLogo.png" />
</p>

## Quick Start
1. Rename keys_to_the_castle.example to keys_to_the_castle.py and enter your [Google AI Studio API key](https://aistudio.google.com/apikey)
2. Install dependencies with 
```bash
   pip install -r requirements.txt
```
3. Run main.py, it will start translating the sample files.

## Customization 
You can easily customize this project to your own needs by editing the prompt_gen.py file and entering your own instructions for the model.

Bear in mind that if you do not enter your own instructions the model ***WILL*** perform badly.

Other places for customization are gemini_csv.py and the prompt, csv_processing.py and the CSV Columns, and tools.py for editing the common functions.