import requests
import pdfplumber
import io
import re
import os
import concurrent.futures
import time

# --- Configuration ---
OUTPUT_DIR = 'Standard_QKP'
MAX_WORKERS = 8
INSTANCE_URL_BASE = "https://cedric.cnam.fr/~soutif/QKP/"
PDF_URL = "https://github.com/phil85/results-for-qkp-benchmark-instances/raw/main/tables/Standard-QKP_detailed_results.pdf"

# --- Step 1: Download and parse the OFV PDF ---
print("Downloading PDF of detailed results...")
resp = requests.get(PDF_URL)
resp.raise_for_status()

print("Extracting and normalizing Best OFV values...")
raw_map = {}
with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
    for i, page in enumerate(pdf.pages):
        if i == 0:
            continue  # Skip the first page as it contains no instance data
        text = page.extract_text()

        lines = text.split("\n")
        inst_line = next((l for l in lines if l.startswith("File ")), None)

        raw_name = inst_line.replace("File ", "").strip()
        header_idx = next((i for i, l in enumerate(lines) if l.startswith("γ ")), None)

        data_tokens = lines[header_idx + 1].split()
        ofv_str = data_tokens[1].replace(",", "")
        raw_map[raw_name] = int(float(ofv_str))

# Normalize to consistent filenames
ofv_map = {}
for raw_name, ofv_int in raw_map.items():
    m = re.match(r"jeu\s+(\d+)\s+(\d+)\s+(\d+)\.txt", raw_name)
    if not m:
        continue
    n_nodes, density_str, idx_str = m.groups()
    file_key = f"jeu_{n_nodes}_{int(density_str)}_{int(idx_str)}.txt"
    ofv_map[file_key] = ofv_int

print(f"Mapped OFV for {len(ofv_map)} instances.")

# --- Step 2: Prepare download tasks ---
n_nodes_list = [100, 200, 300]
densities = {
    100: [25, 50, 75, 100],
    200: [25, 50, 75, 100],
    300: [25, 50]
}
n_instances = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_and_save_instance(n_nodes, density, idx):
    file_name = f"jeu_{n_nodes}_{density}_{idx}.txt"
    url = f"{INSTANCE_URL_BASE}{file_name}"

    for attempt in range(3):
        try:
            print(f"Downloading {file_name} ...")
            resp = requests.get(url)
            resp.raise_for_status()
            break
        except Exception as e:
            print(f"Error with {file_name}: {e}")
            print(f"Retrying ({attempt+1}/3)...")
            time.sleep(attempt * 2)
    else:
        print(f"Failed to download {file_name} after 3 attempts.")
        return
    lines = resp.text.split('\n')
    nn = int(lines[1].strip())
    edges = []
    linear = [int(v) for v in lines[2].split() if v]
    for i in range(nn):
        edges.append((i, i, linear[i]))
    for i in range(nn):
        quad = [int(v) for v in lines[3 + i].split() if v]
        for j in range(i + 1, nn):
            val = quad[j - (i + 1)]
            if val:
                edges.append((i, j, val))

    budget = int(lines[4 + nn].strip())
    weights = [int(v) for v in lines[5 + nn].split() if v]

    out_path = os.path.join(OUTPUT_DIR, file_name)
    with open(out_path, 'w') as f:
        f.write(f"{nn} {len(edges)} int\n")
        for i, j, val in edges:
            f.write(f"{i} {j} {val:.6f}\n")
        f.write(" ".join(str(w) for w in weights) + "\n")
        f.write(f"{budget}\n")
        f.write(f"{ofv_map[file_name]}\n")

# --- Step 3: Run in parallel ---
tasks = [(n_nodes, density, idx)
         for n_nodes in n_nodes_list
         for density in densities[n_nodes]
         for idx in range(1, n_instances + 1)]

print(f"Starting download of {len(tasks)} instances with {MAX_WORKERS} workers...")

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_and_save_instance, *task) for task in tasks]
    for future in concurrent.futures.as_completed(futures):
        pass

print("Done.")
