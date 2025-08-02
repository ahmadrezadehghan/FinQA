#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script lives in the same folder as all your .xlsx exports.
It will automatically find every .xlsx in its own directory,
preprocess the "Message" column (remove emojis, URLs, punctuation,
ellipses, stopwords, lowercase), and then save everything
to processed_telegram_data.xlsx in that same folder.
"""

import os
import re
import string
from glob import glob

import pandas as pd

# --- CONFIGURATION ---

# Directory where this script lives (and where your .xlsx files are)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Name of the final consolidated file
OUTPUT_FILE = 'processed_telegram_data.xlsx'

# Stopwords to drop
STOPWORDS = {'a', 'the', 'at', 'in', 'and'}

# Emoji and URL patterns
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "]+",
    flags=re.UNICODE
)
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')

def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = EMOJI_PATTERN.sub('', text)
    text = URL_PATTERN.sub('', text)
    text = text.replace('...', ' ')
    # strip all punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # drop stopwords
    tokens = [tok for tok in text.split() if tok not in STOPWORDS]
    return re.sub(r'\s+', ' ', ' '.join(tokens)).strip()

def main():
    # find all .xlsx except our output file
    pattern = os.path.join(SCRIPT_DIR, '*.xlsx')
    all_files = glob(pattern)
    excel_files = [
        fn for fn in all_files
        if os.path.basename(fn) != OUTPUT_FILE
    ]

    if not excel_files:
        print(f"No .xlsx files found in {SCRIPT_DIR!r}.")
        return

    processed = []
    for path in excel_files:
        print(f"→ Loading {os.path.basename(path)}")
        try:
            df = pd.read_excel(path, engine='openpyxl')
        except Exception as e:
            print(f"   ✗ Couldn't read {path}: {e}")
            continue

        if 'Message' not in df.columns:
            print(f"   ⚠ Skipping (no Message column)")
            continue

        df['Message'] = df['Message'].fillna('').map(preprocess_text)
        df = df[df['Message'] != '']  # drop empty
        processed.append(df)

    if not processed:
        print("No data left after cleaning, exiting.")
        return

    print("→ Concatenating and saving to", OUTPUT_FILE)
    result = pd.concat(processed, ignore_index=True)
    out_path = os.path.join(SCRIPT_DIR, OUTPUT_FILE)
    try:
        result.to_excel(out_path, index=False, engine='openpyxl')
        print("✅ Done!")
    except Exception as e:
        print("✗ Error saving:", e)

if __name__ == '__main__':
    main()
