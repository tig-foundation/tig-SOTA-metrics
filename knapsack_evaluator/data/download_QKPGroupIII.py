import requests
import pdfplumber
import re
import os
import io
import shutil
import multiprocessing
import zipfile

# --- Configuration ---
ZIP_URL = "https://leria-info.univ-angers.fr/%7Ejinkao.hao/QKPDATA/QKPGroupIII.zip"
PDF_URL = "https://raw.githubusercontent.com/phil85/results-for-qkp-benchmark-instances/main/tables/QKPGroupIII_detailed_results.pdf"
OUT_DIR = 'QKPGroupIII'
RAW_DIR = os.path.join(OUT_DIR, 'raw_data')
NUM_WORKERS = 8

# 1) Download & parse the PDF
print("Downloading Group III detailed results PDF...")
resp = requests.get(PDF_URL)
resp.raise_for_status()

print("Extracting Best OFV values for Group III...")
ofv_map = {}
with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
    for i, page in enumerate(pdf.pages):
        if i == 0:
            continue  # Skip the first page as it contains no instance data
        lines = (page.extract_text() or "").split("\n")

        # e.g. "File 5000 25 1.txt"
        inst_line = next((l for l in lines if l.startswith("File ")))
        raw_name = inst_line.replace("File ", "").strip()

        # locate the γ header line
        header_idx = next((i for i, l in enumerate(lines) if l.startswith("γ ")))

        tokens = lines[header_idx + 1].split()

        # parse OFV, remove commas, then to int
        ofv_val = int(float(tokens[1].replace(",", "")))

        # normalize "5000 25 1.txt" → "5000_25_1.txt"
        m = re.match(r"(\d+)\s+(\d+)\s+(\d+)\.txt", raw_name)
        n, d, idx = m.groups()
        key = f"{n}_{int(d)}_{int(idx)}.txt"
        ofv_map[key] = ofv_val
print(f"Mapped OFV for {len(ofv_map)} instances")

# 2) Prepare directories
os.makedirs(RAW_DIR, exist_ok=True)

# 3) Download & unzip the raw data zip into RAW_DIR
print("Downloading raw Group III zip...")
resp = requests.get(ZIP_URL)
resp.raise_for_status()

print("Extracting raw Group III data...")
with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
    zf.extractall(RAW_DIR)

# 4) Process each instance file
n_nodes_list = [5000, 6000]
densities = {5000: [25, 50, 75, 100],
            6000: [25, 50, 75, 100]}

tasks = []
for n_nodes in n_nodes_list:
    for density in densities[n_nodes]:
        for instance in range(1, 6):
            tasks.append(f"{n_nodes}_{density}_{instance}")

def process_file(name):
    print(f"Processing {name}")
    lines = open(os.path.join(RAW_DIR, 'QKPGroupIII', f"{name}.txt"), 'r').readlines()

    # Get number of nodes and edges
    actual_nodes = int(lines[1])
    # Get linear utilities
    edges = []
    linear_utilities = [int(v) for v in lines[3].strip('\n').split(' ') if v != '']
    for i in range(actual_nodes):
        edges += [(i, i, linear_utilities[i])]
    # Get quadratic utilities
    for i in range(actual_nodes):
        quadratic_utilities = [int(v) for v in lines[4 + i].strip('\n').split(' ') if v != '']
        for j in range(i + 1, actual_nodes):
            edges += [(i, j, quadratic_utilities[j - (i + 1)])]

    # Remove edges with utility of zero
    edges = [edge for edge in edges if edge[2] != 0]

    # Get weights
    budget = int(lines[6 + actual_nodes].strip('\n'))
    weights = [int(v) for v in lines[7 + actual_nodes].strip('\n').split(' ') if v != '']

    # Write output file
    txt_name = f"{name}.txt"
    with open(os.path.join(OUT_DIR, txt_name), 'w') as out:
        out.write(f"{actual_nodes} {len(edges)} int\n")
        for i, j, val in edges:
            out.write(f"{i} {j} {val:.6f}\n")
        out.write(" ".join(str(w) for w in weights) + "\n")
        out.write(f"{budget}\n")
        out.write(f"{ofv_map[txt_name]}\n")

with multiprocessing.Pool(NUM_WORKERS) as pool:
    pool.map(process_file, tasks)

print("Removing raw data")
shutil.rmtree(RAW_DIR, ignore_errors=True)

print("Done.")