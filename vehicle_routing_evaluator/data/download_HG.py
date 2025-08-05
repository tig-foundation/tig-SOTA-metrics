###
# Download Homberger and Gehring .txt files and matching .sol files
### 

import concurrent.futures
import time
import io
import itertools
import pandas as pd
import pdfplumber
import re
import requests
import os

if not os.path.exists('HG'):
    os.makedirs('HG')

# Download Dataset
MAX_WORKERS = 8
BASE_URL = "http://vrp.galgos.inf.puc-rio.br/media/com_vrp/instances/HG/"

def download_instance(download_url, save_path):
    for i in range(3):
        try:
            print('Downloading ' + download_url)
            resp = requests.get(download_url)
            resp.raise_for_status()
            break
        except Exception as e:
            print(f"Error downloading {download_url}: {e}")
            print(f"Retrying {download_url}: {i+1} of 3")
            time.sleep(i * 2)
    else:
        print(f"Failed to download {download_url} after 3 attempts.")
        return
    with open(save_path, 'w') as f:
        f.write(resp.text)

tasks = []
for combo in itertools.product(
    ['C1', 'C2', 'R1', 'R2', 'RC1', 'RC2'],
    [2, 4, 6, 8, 10],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [".txt", ".sol"]
):
    name = f"{combo[0]}_{combo[1]}_{combo[2]}{combo[3]}"
    url = f"{BASE_URL}{name}"
    save_path = os.path.join('HG', name)
    tasks.append((url, save_path))

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_instance, url, save_path) for url, save_path in tasks]
    for future in concurrent.futures.as_completed(futures):
        pass


# Download SOTA results
print("Downloading SOTA results")
PDF_URL = "https://www.cirrelt.ca/documentstravail/cirrelt-2011-61.pdf"

resp = requests.get(PDF_URL)
resp.raise_for_status()
with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
    for page in pdf.pages:
        text = page.extract_text() or ""
        if "Table 11" in text:
            table = page.extract_table()
            break
    else:
        raise ValueError("Table 11 not found in the SOTA results PDF.")


# Parse the table into a DataFrame
print("Parsing SOTA results")
headers = table[0]
method_names = [h.strip() for h in headers[1:]]
records = []

for row in table[1:]:
    # Parse n and vehicle options
    tokens0 = re.split(r"\s+", (row[0] or "").strip())
    if len(tokens0) < 2:
        continue
    n = int(tokens0[0])
    vehicle_opts = [int(x) for x in tokens0[1:]]
    # Extract each method column
    for col_idx, method in enumerate(method_names, start=1):
        tokens = re.split(r"\s+", (row[col_idx] or "").strip())
        # Pair up used & distance
        pairs = []
        for i in range(0, len(tokens)-1, 2):
            try:
                used = int(tokens[i])
                dist = float(tokens[i+1])
            except ValueError:
                continue
            pairs.append((used, dist))
        # Record entries matching vehicle options
        for idx, (used, dist) in enumerate(pairs[:len(vehicle_opts)]):
            inst = f"{method.upper()}_{int(n/100)}_{idx+1}"
            records.append({
                'instance': inst,
                # 'n': n,
                # 'num_veh': vehicle_opts[idx],
                # 'method': method.upper(),
                'nv': used,
                'distance': dist
            })
sota_df = pd.DataFrame(records)

# Read baseline results
print("Reading baseline results")
data = []
for combo in itertools.product(
    ['C1', 'C2', 'R1', 'R2', 'RC1', 'RC2'],
    [2, 4, 6, 8, 10],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
):
    name = f"{combo[0]}_{combo[1]}_{combo[2]}"
    with open(os.path.join('HG', name + '.sol'), 'r') as f:
        lines = f.read().splitlines()
    fleet_size = sum(1 for line in lines if re.match(r"(?i)^route\s+#", line))
    distance = None
    for ln in reversed(lines):
        cap = re.search(r"(?i)cost\s+(\d+(?:\.\d+)?)", ln)
        if cap:
            val = float(cap.group(1))
            distance = int(round(val))
            break
    else:
        raise ValueError(f"Baseline distance not found in {name}.sol file.")
    data.append({
        'instance': name,
        'baseline_fleet_size': fleet_size,
        'baseline_distance': distance
    })

baseline_df = pd.DataFrame(data)

# Merge SOTA + baseline and save results
print("Merging SOTA + baseline results, and saving to sota.csv")
merged_df = baseline_df.merge(sota_df, on='instance', how='left')
merged_df['rpd'] = 100 * (merged_df['distance'] - merged_df['baseline_distance']) / merged_df['distance']
merged_df.to_csv(f"HG/sota.csv", index=False)

print("Done.")
