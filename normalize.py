import pandas as pd
import numpy as np
import re
import html
import unicodedata
import os
import matplotlib.pyplot as plt

# === 1. Load the data ===
file_path = 'full_data.xlsx'
if not os.path.exists(file_path):
    raise FileNotFoundError(f"'{file_path}' not found. Please ensure the file is in the working directory.")

df = pd.read_excel(file_path, parse_dates=False)

# === 1.a Guarantee datetime type ===
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
# Drop rows where the date failed to parse (optional)
df = df[df['Date'].notna()]

# === 2. Initial EDA ===
print("\n=== Messages per Source (Raw) ===")
print(df['Source'].value_counts())

# 2.1 Daily message volumes
daily_counts = (
    df
    .set_index('Date')
    .resample('D')
    .size()
    .rename('Count')
)
print("\n=== Daily Message Counts (Raw) ===")
print(daily_counts)
plt.figure()
daily_counts.plot(title="Daily Message Counts (Raw)")
plt.tight_layout()
plt.show()

# 2.2 Length/token stats
df['msg_len']      = df['Message'].str.len()
df['token_count'] = df['Message'].str.split().apply(len)
print("\n=== Message Length (Raw) ===")
print(df['msg_len'].describe())
print("\n=== Token Count (Raw) ===")
print(df['token_count'].describe())

# === 3. Advanced Cleaning & Normalization ===
df_clean = df.copy()

# 3.a Sort by timestamp (so identical Date/Timestamps stay adjacent)
df_clean = df_clean.sort_values('Date').reset_index(drop=True)

# 3.b Remove bot heartbeats
heartbeat_pattern = re.compile(r'^(ping|pong|heartbeat|alive)$', re.IGNORECASE)
df_clean = df_clean[~df_clean['Message'].str.match(heartbeat_pattern, na=False)]

# 3.c Filter out very short messages
df_clean = df_clean[df_clean['Message'].str.len() > 3]

# 3.d Normalization function
emoji_pattern = re.compile(
    "[\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "]+", flags=re.UNICODE
)

def normalize_text(text):
    text = str(text)
    text = unicodedata.normalize('NFKC', text)
    text = html.unescape(text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'@\w+|#\w+', '', text)
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = emoji_pattern.sub('', text)
    text = re.sub(r'[^\x00-\x7f]', '', text)
    text = re.sub(r'([.!?])\1+', r'\1', text)
    text = re.sub(r'[`*_~]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

df_clean['Message'] = df_clean['Message'].apply(normalize_text)
df_clean = df_clean[df_clean['Message'].str.len() > 0]

# 3.e Recompute stats
df_clean['msg_len']     = df_clean['Message'].str.len()
df_clean['token_count']= df_clean['Message'].str.split().apply(len)
print("\n=== Message Length (Clean) ===")
print(df_clean['msg_len'].describe())
print("\n=== Token Count (Clean) ===")
print(df_clean['token_count'].describe())

# === 4. Export ===
output_path = 'normalized_output.xlsx'
df_clean.to_excel(output_path, index=False)
print(f"\nCleaned & normalized data saved to '{output_path}'.")
