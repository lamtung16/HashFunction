import pandas as pd

# 1. Combine 1.csv through 7.csv into a single dataframe
file_list = [f"{i}.csv" for i in range(1, 8)]
df_combined = pd.concat([pd.read_csv(file) for file in file_list], ignore_index=True)

# 2. Sort the dataframe by the "host" column
df_sorted = df_combined.sort_values(by="host")

# 3. Filter out rows where status != "Active" AND drop rows with missing hosts
df_filtered = df_sorted[df_sorted["status"] == "Active"].dropna(subset=["host"])

# 4. Group by host and save each group into its own <host>.csv file
for host, group in df_filtered.groupby("host"):
    safe_host = str(host).strip()
    
    # Skip if host name is empty or literal 'nan'
    if not safe_host or safe_host.lower() == "nan":
        continue
        
    # Clean characters that are invalid for Windows/Linux filenames
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        safe_host = safe_host.replace(char, '_')
    
    # Save to CSV
    group.to_csv(f"{safe_host}.csv", index=False)