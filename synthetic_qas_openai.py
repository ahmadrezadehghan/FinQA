#!/usr/bin/env python3
import os
import time
import csv
import json
import pandas as pd
import requests
from tqdm import tqdm

# === CONFIGURATION ===
INPUT_CSV       = 'eda_outputs/cluster_samples_for_labeling.csv'
OUTPUT_CSV      = 'synthetic_qas_by_cluster_hf.csv'
NUM_QAS_PER_MSG = 3
HF_MODEL = 'google/flan-t5-base'

CHUNK_SIZE      = 500
SLEEP_BETWEEN   = 1  # seconds between calls

# Get HF token
HF_TOKEN = os.getenv('HF_TOKEN')
if not HF_TOKEN:
    raise RuntimeError("Please set the HF_TOKEN environment variable with your Hugging Face API token.")
headers = { 'Authorization': f'Bearer {HF_TOKEN}' }
api_url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# Verify input
if not os.path.isfile(INPUT_CSV):
    raise FileNotFoundError(f"Expected clustered sample CSV at {INPUT_CSV}")

# Prepare output CSV
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as fout:
    writer = csv.DictWriter(fout, fieldnames=[
        'cluster','message_id','question','answer','answer_start','source'
    ])
    writer.writeheader()

    msg_id = 0
    for chunk in pd.read_csv(INPUT_CSV, usecols=['cluster','Message'], chunksize=CHUNK_SIZE):
        for _, row in tqdm(chunk.iterrows(), total=len(chunk), desc=f"Batch up to msg {msg_id+len(chunk)}"):
            cluster = row['cluster']
            context = str(row['Message']).replace('\n',' ').strip()
            prompt = f"Generate {NUM_QAS_PER_MSG} question and answer pairs about this text: {context}"
            payload = {
                'inputs': prompt,
                'options': {'wait_for_model': True},
                'parameters': {
                    'do_sample': True,
                    'top_p': 0.95,
                    'num_return_sequences': NUM_QAS_PER_MSG,
                    'max_length': 64
                }
            }
            outputs = []
            try:
                resp = requests.post(api_url, headers=headers, json=payload)
                if resp.status_code != 200:
                    raise ValueError(f"HF API error {resp.status_code}: {resp.text}")
                outputs = resp.json()
            except Exception as e:
                print(f"[Warning] HF API failed msg_id {msg_id}: {e}")

            # Parse and write Q&A
            for out in outputs:
                txt = out.get('generated_text', '').strip() if isinstance(out, dict) else ''
                if '?' in txt:
                    q_part, a_part = txt.split('?',1)
                    question = q_part.strip() + '?'
                    answer   = a_part.strip()
                else:
                    question, answer = txt, ''
                start = context.find(answer) if answer else -1
                writer.writerow({
                    'cluster':      cluster,
                    'message_id':   msg_id,
                    'question':     question,
                    'answer':       answer,
                    'answer_start': start,
                    'source':       'hf_api'
                })
            msg_id += 1
            time.sleep(SLEEP_BETWEEN)

print(f"Done → ~{msg_id*NUM_QAS_PER_MSG} Q&A rows in '{OUTPUT_CSV}'")
