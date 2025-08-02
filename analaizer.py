import os
import sys
import pandas as pd
import numpy as np
import re
import html
import unicodedata
import matplotlib.pyplot as plt

# === 1. Load the data ===
file_path = 'full_data.xlsx'  # adjust if needed
if not os.path.exists(file_path):
    print(f"Error: '{file_path}' not found. Please upload the file or adjust 'file_path'.")
    sys.exit(1)

# Read in—and coerce Date to datetime
df = pd.read_excel(file_path)
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Drop rows where Date couldn't be parsed
df.dropna(subset=['Date'], inplace=True)

# === 2. Inspection ===

# 2a. Messages per source
source_counts = (
    df['Source']
      .value_counts()
      .reset_index()
      .rename(columns={'index': 'Source', 'Source': 'Count'})
)
print("\nMessages per Source:")
print(source_counts.to_string(index=False))

# 2b. Daily message counts via Grouper
daily_counts = (
    df
      .groupby(pd.Grouper(key='Date', freq='D'))
      .size()
      .reset_index(name='Count')
)
print("\nDaily Message Counts (first 10 days):")
print(daily_counts.head(10).to_string(index=False))

# 2c. Plot daily counts
plt.figure(figsize=(10, 4))
plt.plot(daily_counts['Date'], daily_counts['Count'])
plt.title("Daily Message Counts")
plt.xlabel("Date")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# 2d. Message length & token stats
df['msg_len'] = df['Message'].str.len()
length_stats = df['msg_len'].describe().to_frame('Message Length')
print("\nMessage Length Distribution:")
print(length_stats.to_string())

df['token_count'] = df['Message'].str.split().apply(len)
token_stats = df['token_count'].describe().to_frame('Token Count')
print("\nToken Count Distribution:")
print(token_stats.to_string())

# === 3. Cleaning & Filtering ===

# Work on a copy
df_clean = df.drop_duplicates().copy()

# 3a. Remove simple heartbeats
heartbeat_pattern = re.compile(r'^(ping|pong|heartbeat|alive)$', re.IGNORECASE)
df_clean = df_clean[~df_clean['Message'].str.match(heartbeat_pattern)]

# 3b. Drop very short messages
df_clean = df_clean[df_clean['msg_len'] > 3]

# 3c. Normalize unicode & collapse repeated punctuation
df_clean['Message'] = df_clean['Message'].apply(lambda x: unicodedata.normalize('NFKC', x))
df_clean['Message'] = df_clean['Message'].str.replace(r'([.!?])\1+', r'\1', regex=True)

# 3d. Unescape HTML entities
df_clean['Message'] = df_clean['Message'].apply(html.unescape)

# 3e. Remove emojis
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "]+", flags=re.UNICODE
)
df_clean['Message'] = df_clean['Message'].str.replace(emoji_pattern, '', regex=True)

print(f"\nOriginal rows: {len(df):,}")
print(f"Cleaned  rows: {len(df_clean):,}")

# === 4. Write all outputs to a new Excel file ===
output_file = 'telegram_analysis_outputs.xlsx'
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    source_counts.to_excel(writer, sheet_name='Messages_per_Source', index=False)
    daily_counts.to_excel(writer, sheet_name='Daily_Message_Counts', index=False)
    length_stats.to_excel(writer, sheet_name='Message_Length_Stats')
    token_stats.to_excel(writer, sheet_name='Token_Count_Stats')
    df_clean.to_excel(writer, sheet_name='Cleaned_Data', index=False)

print(f"\nAll outputs written to '{output_file}'")
