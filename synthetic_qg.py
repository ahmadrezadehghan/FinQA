```python
#!/usr/bin/env python3
"""
Synthetic Question Generation for QA Dataset Expansion

This script reads a CSV of manually-annotated contexts (your gold set),
generates synthetic Q&A pairs for each context using a Hugging Face
question-generation pipeline, and writes the combined output to a new CSV.

Usage:
    pip install transformers torch pandas
    python synthetic_qg.py \
        --input gold_annotations.csv \
        --output synthetic_qas.csv \
        --max-samples 500

The input CSV must have at least these columns:
    - context: the full text to generate questions from
    - [optional] any other metadata you wish to carry through

The output CSV will contain:
    - context
    - question
    - answer
    - answer_start (character index in context)
    - source: 'synthetic'
"""

import argparse
import pandas as pd
from transformers import pipeline

def main(args):
    # Load the manually-annotated gold set
    df = pd.read_csv(args.input)
    if 'context' not in df.columns:
        raise ValueError("Input CSV must have a 'context' column.")

    # Initialize the question-generation pipeline
    qg = pipeline(
        "question-generation",
        model="valhalla/t5-small-qa-qg-hl",
        device=0 if args.use_cuda else -1
    )

    records = []
    for i, row in df.iterrows():
        if args.max_samples and i >= args.max_samples:
            break
        context = str(row['context'])
        try:
            qas = qg(context)
        except Exception as e:
            print(f"[Warning] QG failed on row {i}: {e}")
            continue

        for qa in qas:
            answer = qa.get('answer', '').strip()
            answer_start = context.find(answer) if answer else -1
            records.append({
                'context': context,
                'question': qa.get('question', '').strip(),
                'answer': answer,
                'answer_start': answer_start,
                'source': 'synthetic'
            })

    out_df = pd.DataFrame.from_records(records)
    out_df.to_csv(args.output, index=False)
    print(f"Generated {len(out_df)} synthetic Q&A pairs → {args.output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Expand QA dataset with synthetic question generation"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to manually-annotated gold CSV (must have 'context' column)"
    )
    parser.add_argument(
        "--output", "-o", default="synthetic_qas.csv",
        help="Path to write the synthetic Q&A CSV"
    )
    parser.add_argument(
        "--max-samples", "-m", type=int, default=0,
        help="Maximum number of contexts to process (0 = all)"
    )
    parser.add_argument(
        "--use-cuda", action="store_true",
        help="Run model on GPU if available"
    )
    args = parser.parse_args()
    main(args)
