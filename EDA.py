import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# 1. Load & Inspect
excel_path = 'final.xlsx'  # adjust path if needed
if not os.path.exists(excel_path):
    raise FileNotFoundError(f"File not found: {excel_path}")

df = pd.read_excel(excel_path, parse_dates=['Date'])

# Quick inspection
print("First 5 rows:")
print(df.head(), "\n")
print("msg_len & token_count stats:")
print(df[['msg_len', 'token_count']].describe(), "\n")
print("Source distribution:")
print(df['Source'].value_counts(), "\n")

# Derive time features
df['hour'] = df['Date'].dt.hour
df['weekday'] = df['Date'].dt.day_name()

# 2. Visualizations

# a) Hour of day distribution
plt.figure(figsize=(8,4))
plt.hist(df['hour'], bins=24, edgecolor='black')
plt.title('Message Distribution by Hour of Day')
plt.xlabel('Hour')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# b) Weekday distribution
plt.figure(figsize=(8,4))
plt.hist(df['weekday'], bins=len(df['weekday'].unique()), edgecolor='black')
plt.title('Message Distribution by Weekday')
plt.xlabel('Weekday')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# c) Message length histogram
plt.figure(figsize=(8,4))
plt.hist(df['msg_len'], bins=50, edgecolor='black')
plt.title('Message Length Distribution')
plt.xlabel('Message Length')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# d) Token count histogram
plt.figure(figsize=(8,4))
plt.hist(df['token_count'], bins=50, edgecolor='black')
plt.title('Token Count Distribution')
plt.xlabel('Token Count')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

# 3. Clustering by Content

# Vectorize messages with TF-IDF
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X = vectorizer.fit_transform(df['Message'].astype(str))

# Apply K-Means
n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# Output cluster sizes
print("Cluster sizes:")
print(df['cluster'].value_counts(), "\n")

# Show top terms per cluster
terms = vectorizer.get_feature_names_out()
order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

for i in range(n_clusters):
    top_terms = [terms[idx] for idx in order_centroids[i, :10]]
    print(f"Cluster {i} top terms: {top_terms}")
