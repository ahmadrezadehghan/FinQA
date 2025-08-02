#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Normalize column C ("Message") of processed_telegram_data.xlsx:
 - Unicode NFKC normalization
 - Remove *all* emojis (including 🪙, ⏰, etc.)
 - Remove URLs
 - Lowercase
 - Strip punctuation & digits
 - Remove any non-English letters
 - Collapse whitespace
 - Drop messages under 20 characters long
Outputs processed_telegram_data_normalized.xlsx
"""

import os
import re
import string
import unicodedata
import pandas as pd

# --- CONFIGURATION ---
INPUT_FILE  = 'out.xlsx'
OUTPUT_FILE = 'processed_telegram_data_normalizedV7.xlsx'
MIN_LENGTH  = 20  # minimum message length in characters

# Comprehensive emoji regex
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"  # Misc Symbols & Pictographs
    "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
    "\U0001F1E0-\U0001F1FF"  # Regional Indicator (flags)
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols & Pictographs
    "\U0001FA90-\U0001FAFF"  # Extended Pictographic (coins, etc.)
    "\u2300-\u23FF"          # Misc Technical (e.g. ⏰)
    "\u2600-\u26FF"          # Misc symbols
    "\u2700-\u27BF"          # Dingbats
    "\uFE0F"                 # Variation Selector-16
    "]+",
    flags=re.UNICODE
)
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    # 1) Unicode NFKC
    text = unicodedata.normalize('NFKC', text)
    # 2) Remove emojis
    text = EMOJI_PATTERN.sub('', text)
    # 3) Remove URLs
    text = URL_PATTERN.sub('', text)
    # 4) Lowercase
    text = text.lower()
    # 5) Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # 6) Remove digits
    text = re.sub(r'\d+', '', text)
    # 7) Remove non-English letters (keep a–z and spaces only)
    text = re.sub(r'[^a-z\s]', '', text)
    # 8) Collapse whitespace
    return re.sub(r'\s+', ' ', text).strip()

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"✗ File not found: {INPUT_FILE!r}")
        return

    print(f"→ Loading {INPUT_FILE}")
    df = pd.read_excel(INPUT_FILE, engine='openpyxl')

    # Identify the message column
    col = 'Message' if 'Message' in df.columns else df.columns[2]
    print(f"→ Normalizing column {col!r} ({len(df)} rows)...")

    # Normalize text
    df[col] = df[col].fillna('').map(normalize_text)

    # Drop empty messages
    before = len(df)
    df = df[df[col] != '']
    dropped_empty = before - len(df)
    if dropped_empty:
        print(f"→ Dropped {dropped_empty} empty rows")

    # Drop messages shorter than MIN_LENGTH
    before = len(df)
    df = df[df[col].str.len() >= MIN_LENGTH]
    dropped_short = before - len(df)
    if dropped_short:
        print(f"→ Dropped {dropped_short} rows under {MIN_LENGTH} characters")

    # Save the cleaned data
    print(f"→ Saving to {OUTPUT_FILE}")
    df.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
    print("✅ Done. All emojis, non-English letters, and short messages removed.")

if __name__ == '__main__':
    main()
