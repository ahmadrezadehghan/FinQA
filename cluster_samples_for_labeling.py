import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# === CONFIG ===
excel_path = r'C:\Users\AHMAD\Desktop\web_perper\training\final.xlsx'
output_dir = 'Clustered'
msg_len_thresh = 500
token_count_thresh = 100
major_source = 'degenpump_crypto_pump_signals'
n_clusters = 5
n_samples_per_cluster = 10
random_state = 42

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# 1. Load data
df = pd.read_excel(excel_path, parse_dates=['Date'])

# 2. Outlier handling: filter overly long messages
df_filtered = df[
    (df['msg_len'] <= msg_len_thresh) &
    (df['token_count'] <= token_count_thresh)
].copy()

# 3. Clustering by content
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X = vectorizer.fit_transform(df_filtered['Message'].astype(str))
kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
df_filtered['cluster'] = kmeans.fit_predict(X)

# 4. Source balancing: down-sample dominant source
major_df = df_filtered[df_filtered['Source'] == major_source]
minor_df = df_filtered[df_filtered['Source'] != major_source]
if len(minor_df) > 0:
    major_down = major_df.sample(n=len(minor_df), random_state=random_state)
    df_balanced = pd.concat([major_down, minor_df]).reset_index(drop=True)
else:
    df_balanced = df_filtered.copy()

# Optional: Compute sampling weights
freq = df_balanced['Source'].value_counts()
df_balanced['source_weight'] = df_balanced['Source'].map(lambda x: 1.0 / freq[x])

# 5. Encode Source as numeric feature
le = LabelEncoder()
df_balanced['source_id'] = le.fit_transform(df_balanced['Source'])

# 6. Per-cluster train/test splits (no stratify to avoid single-sample issues)
for cluster_label in sorted(df_balanced['cluster'].unique()):
    sub_df = df_balanced[df_balanced['cluster'] == cluster_label]
    if len(sub_df) < 20:
        continue  # skip tiny clusters
    train_df, test_df = train_test_split(
        sub_df,
        test_size=0.1,
        random_state=random_state
    )
    train_df.to_csv(os.path.join(output_dir, f'cluster_{cluster_label}_train.csv'), index=False)
    test_df.to_csv(os.path.join(output_dir, f'cluster_{cluster_label}_test.csv'), index=False)

# 7. Sample messages for manual Q&A labeling
samples = (
    df_balanced
    .groupby('cluster', group_keys=False)
    .apply(lambda grp: grp.sample(n=min(n_samples_per_cluster, len(grp)), random_state=random_state))
)
samples.to_csv(os.path.join(output_dir, 'cluster_samples_for_labeling.csv'), index=False)

print(f"EDA & preprocessing completed. Outputs saved in: {output_dir}")
