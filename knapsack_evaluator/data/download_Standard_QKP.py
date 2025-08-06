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
INSTANCE_URL_BASE = "https://cedric.cnam.fr/~soutif/QKP"
PDF_URL = "https://github.com/phil85/results-for-qkp-benchmark-instances/raw/main/tables/Standard-QKP_detailed_results.pdf"


n_nodes_list = [100, 200, 300]
densities = {
    100: [25, 50, 75, 100],
    200: [25, 50, 75, 100],
    300: [25, 50]
}
n_instances = 10
SOTA_algos = ('QKBP', 'RG', 'IHEA', 'LDP', 'DP', 'QK', 'Gurobi', 'Hexaly')
combos = [(n_nodes, density, idx)
         for n_nodes in n_nodes_list
         for density in densities[n_nodes]
         for idx in range(1, n_instances + 1)]

# --- Step 1: Download and parse the OFV PDF ---
print("Downloading PDF of detailed results...")
resp = requests.get(PDF_URL)
resp.raise_for_status()

print("Extracting Best OFV and SOTA results...")
instance_data = {}
page = 1
with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
    for nn, d, idx in combos:
        crop = pdf.pages[page].crop((40, 145, 535, 195))
        table = crop.extract_table({
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "snap_tolerance": 3,
            "join_tolerance": 3,
        })
        if table[0][0] == 'γ BestOFV':
            table[0][:1] = list(table[0][0].split(' '))
            table[2][:1] = list(table[2][0].split(' '))
        assert tuple(table[0]) == (('γ', 'BestOFV') + SOTA_algos + SOTA_algos)
        assert tuple(row[0] for i, row in enumerate(table) if i != 2) == ('γ', '', '', 'Avg', 'Min', 'Max')
        row = table[2]
        instance_data[f"standard_qkp_{nn}_{d}_{idx}.txt"] = {
            'ofv': int(float(row[1].replace(',', ''))),
            'gaps': {
                algo: None if row[2 + j] == '—' else float(row[2 + j].replace(',', ''))
                for j, algo in enumerate(SOTA_algos)
            },
            'runtimes': {
                algo: None if row[2 + len(SOTA_algos) + j] == '—' else float(row[2 + len(SOTA_algos) + j])
                for j, algo in enumerate(SOTA_algos)
            }
        }
        page += 1

print(f"Extracted data for {len(instance_data)} instances.")

# --- Step 2: Prepare download tasks ---

os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_and_save_instance(n_nodes, density, idx):
    instance = f"{n_nodes}_{density}_{idx}.txt"
    url = f"{INSTANCE_URL_BASE}/jeu_{instance}"

    for attempt in range(3):
        try:
            print(f"Downloading {instance} ...")
            resp = requests.get(url)
            resp.raise_for_status()
            break
        except Exception as e:
            print(f"Error with {instance}: {e}")
            print(f"Retrying ({attempt+1}/3)...")
            time.sleep(attempt * 2)
    else:
        print(f"Failed to download {instance} after 3 attempts.")
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

    out_path = os.path.join(OUTPUT_DIR, instance)
    with open(out_path, 'w') as f:
        f.write(f"{nn} {len(edges)} int\n")
        for i, j, val in edges:
            f.write(f"{i} {j} {val:.6f}\n")
        f.write(" ".join(str(w) for w in weights) + "\n")
        f.write(f"{budget}\n")
        f.write(f"{instance_data[instance]['ofv']}\n")

# --- Step 3: Run in parallel ---
print(f"Starting download of {len(combos)} instances with {MAX_WORKERS} workers...")

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_and_save_instance, *task) for task in combos]
    for future in concurrent.futures.as_completed(futures):
        pass

print("Writing SOTA results ...")
with open(os.path.join(OUTPUT_DIR, 'sota.csv'), 'w') as f:
    f.write('instance,algorithm,gap,runtime\n')
    for instance in instance_data:
        for algo in instance_data[instance]['gaps']:
            f.write(f"{instance},{algo},{instance_data[instance]['gaps'][algo]},{instance_data[instance]['runtimes'][algo]}\n")

print("Done.")
