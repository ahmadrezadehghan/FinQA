#!/usr/bin/env python3
import os
# Disable any HTTP/SOCKS proxies
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('https_proxy', None)

import time
import csv
import json
import pandas as pd
import openai
from tqdm import tqdm

# === CONFIGURATION ===
INPUT_CSV       = 'eda_outputs/cluster_samples_for_labeling.csv'
OUTPUT_CSV      = 'synthetic_qas_by_cluster.csv'
NUM_QAS_PER_MSG = 3
PRIMARY_MODEL   = 'gpt-4.1'
FALLBACK_MODEL  = 'gpt-3.5-turbo-16k'
SLEEP_BETWEEN   = 1
CHUNK_SIZE      = 500

# Load your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")

# Verify input file exists
if not os.path.isfile(INPUT_CSV):
    raise FileNotFoundError(f"Expected clustered sample CSV at {INPUT_CSV}")

# Prepare output CSV
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as fout:
    writer = csv.DictWriter(fout, fieldnames=[
        'cluster', 'message_id', 'question', 'answer', 'answer_start', 'source'
    ])
    writer.writeheader()

    msg_id = 0
    # Stream through sampled messages
    for chunk in pd.read_csv(INPUT_CSV, usecols=['cluster', 'Message'], chunksize=CHUNK_SIZE):
        for _, row in tqdm(chunk.iterrows(), total=len(chunk),
                           desc=f"Up to msg {msg_id + len(chunk)}"):
            cluster = row['cluster']
            context = str(row['Message']).replace('\n', ' ').strip()
            prompt  = (
                f"Context:\n\"{context}\"\n\n"
                f"Generate {NUM_QAS_PER_MSG} question-answer pairs about the above context. "
                "Return a JSON array of objects with keys 'question' and 'answer'."
            )
            messages = [
                {"role": "system", "content": "You are a helpful assistant that generates Q&A pairs."},
                {"role": "user", "content": prompt}
            ]

            # Attempt using primary model, fall back on quota errors
            model_to_use = PRIMARY_MODEL
            try:
                resp = openai.chat.completions.create(
                    model=model_to_use,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=256
                )
            except Exception as e:
                err_text = str(e)
                if "insufficient_quota" in err_text or "quota" in err_text.lower():
                    print(f"[Quota exceeded on {PRIMARY_MODEL}, falling back to {FALLBACK_MODEL}]")
                    model_to_use = FALLBACK_MODEL
                    time.sleep(1)
                    try:
                        resp = openai.chat.completions.create(
                            model=model_to_use,
                            messages=messages,
                            temperature=0.7,
                            max_tokens=256
                        )
                    except Exception as e2:
                        print(f"[Error] fallback also failed: {e2}")
                        time.sleep(SLEEP_BETWEEN)
                        continue
                else:
                    print(f"[Error] API error on model {model_to_use}: {err_text}")
                    time.sleep(SLEEP_BETWEEN)
                    continue

            text = resp.choices[0].message.content.strip()
            try:
                qas = json.loads(text)
            except json.JSONDecodeError as jde:
                print(f"[Warning] JSON parse error msg_id {msg_id}: {jde}")
                print("Raw output:", text)
                time.sleep(SLEEP_BETWEEN)
                continue

            # Write out each synthetic Q&A pair
            for qa in qas:
                question     = qa.get('question', '').strip()
                answer       = qa.get('answer', '').strip()
                answer_start = context.find(answer) if answer else -1
                writer.writerow({
                    'cluster':      cluster,
                    'message_id':   msg_id,
                    'question':     question,
                    'answer':       answer,
                    'answer_start': answer_start,
                    'source':       model_to_use
                })

            msg_id += 1
            time.sleep(SLEEP_BETWEEN)

print(f"Done → Generated approx. {msg_id * NUM_QAS_PER_MSG} rows in '{OUTPUT_CSV}'")
