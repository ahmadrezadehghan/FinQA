#!/usr/bin/env python3
"""
synthetic_qas_openai.py

Generate synthetic Q&A pairs from your Telegram messages dataset
using the OpenAI API for question-generation. This avoids needing
HF tokens or local transformer installations.

Dependencies:
    pip install openai pandas tqdm

Setup:
    1. Export your OpenAI API key:
       - PowerShell:
           $Env:OPENAI_API_KEY="your_openai_api_key_here"
       - cmd.exe:
           set OPENAI_API_KEY=your_openai_api_key_here

Usage:
    python synthetic_qas_openai.py
"""

import os
import time
import csv
import json
import pandas as pd
import openai
from tqdm import tqdm

# === CONFIGURATION ===
CSV_PATH        = 'normalized_output.csv'    # Your CSV of messages (exported from Excel)
OUTPUT_CSV      = 'synthetic_qas_openai.csv' # Where to save synthetic Q&As
NUM_QAS_PER_MSG = 3                          # Number of Q&A pairs per message
CHUNK_SIZE      = 5000                       # Rows per API batch
MODEL_NAME      = 'gpt-3.5-turbo'            # Or another OpenAI chat-capable model
SLEEP_BETWEEN  = 1                           # Seconds to wait between API calls

# Ensure API key is set
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")

# Load or convert CSV
if not os.path.isfile(CSV_PATH):
    # Try reading Excel and converting
    if os.path.isfile('normalized_output.xlsx'):
        df_temp = pd.read_excel('normalized_output.xlsx', parse_dates=['Date'])
        df_temp.to_csv(CSV_PATH, index=False)
        del df_temp
    else:
        raise FileNotFoundError("Neither normalized_output.csv nor .xlsx found.")

# Prepare output file
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as fout:
    writer = csv.DictWriter(fout, fieldnames=[
        'message_id','context','question','answer','answer_start','source'
    ])
    writer.writeheader()

    msg_id = 0
    # Stream through messages in batches
    for start in range(0, sum(1 for _ in open(CSV_PATH)) - 1, CHUNK_SIZE):
        df_chunk = pd.read_csv(CSV_PATH, usecols=['Message'], skiprows=range(1, start+1), nrows=CHUNK_SIZE)
        for _, row in tqdm(df_chunk.iterrows(), total=len(df_chunk), desc=f"Batch {start//CHUNK_SIZE+1}"):
            context = str(row['Message']).replace('\n', ' ').strip()
            prompt = (
                f"Context:\n\"{context}\"\n\n"
                f"Generate {NUM_QAS_PER_MSG} question-answer pairs about the above context. "
                "Provide output as a JSON list of objects with keys 'question' and 'answer'."
            )
            try:
                resp = openai.ChatCompletion.create(
                    model=MODEL_NAME,
                    messages=[{"role": "system", "content": "You are a helpful assistant for generating Q&A pairs."},
                              {"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=256
                )
                text = resp.choices[0].message.content.strip()
                data = json.loads(text)
            except Exception as e:
                print(f"[Warning] API error on msg_id {msg_id}: {e}")
                time.sleep(SLEEP_BETWEEN)
                continue

            for qa in data:
                question = qa.get('question', '').strip()
                answer   = qa.get('answer', '').strip()
                answer_start = context.find(answer) if answer else -1
                writer.writerow({
                    'message_id':   msg_id,
                    'context':      context,
                    'question':     question,
                    'answer':       answer,
                    'answer_start': answer_start,
                    'source':       'openai'
                })
            msg_id += 1
            time.sleep(SLEEP_BETWEEN)

print(f"Done → Generated approx. {msg_id * NUM_QAS_PER_MSG} Q&A pairs in '{OUTPUT_CSV}'")
