import pandas as pd
import glob
import os

# 1. Find all Excel files in the working directory
excel_files = glob.glob(os.path.join(os.getcwd(), "*.xls*"))

# 2. Exclude the output file if it already exists
output_filename = "out.xlsx"
excel_files = [f for f in excel_files if os.path.basename(f) != output_filename]

# 3. Read each file into a DataFrame
dfs = []
for file in excel_files:
    df = pd.read_excel(file)
    dfs.append(df)

# 4. Concatenate all DataFrames (preserving header and resetting index)
if dfs:
    combined_df = pd.concat(dfs, ignore_index=True)
else:
    combined_df = pd.DataFrame(columns=["Date", "Source", "Message"])

# 5. Write to out.xlsx
combined_df.to_excel(output_filename, index=False)

print(f"Combined {len(dfs)} files into '{output_filename}'.")
