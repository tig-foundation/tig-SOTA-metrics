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
OUTPUT_DIR = 'QKPGroupIII'
RAW_DIR = os.path.join(OUTPUT_DIR, 'raw_data')
NUM_WORKERS = 8

n_nodes_list = [5000, 6000]
densities = {5000: sorted(map(str, [25, 50, 75, 100])),
            6000: sorted(map(str, [25, 50, 75, 100]))}
n_instances = 5
SOTA_algos = ('QKBP', 'RG', 'IHEA', 'LDP', 'DP', 'QK', 'Gurobi', 'Hexaly')
combos = [(n_nodes, density, idx)
         for n_nodes in n_nodes_list
         for density in densities[n_nodes]
         for idx in range(1, n_instances + 1)]

# 1) Download & parse the PDF
print("Downloading Group III detailed results PDF...")
resp = requests.get(PDF_URL)
resp.raise_for_status()

print("Extracting Best OFV and SOTA results...")
instance_data = {}
page = 1
with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
    for nn, d, idx in combos:
        crop = pdf.pages[page].crop((35, 142, 535, 192))
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
        instance_data[f"{nn}_{d}_{idx}.txt"] = {
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
        
print(f"Extracted data for {len(instance_data)} instances")

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
def process_file(instance):
    print(f"Processing {instance}")
    lines = open(os.path.join(RAW_DIR, 'QKPGroupIII', instance), 'r').readlines()

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
    with open(os.path.join(OUTPUT_DIR, instance), 'w') as out:
        out.write(f"{actual_nodes} {len(edges)} int\n")
        for i, j, val in edges:
            out.write(f"{i} {j} {val:.6f}\n")
        out.write(" ".join(str(w) for w in weights) + "\n")
        out.write(f"{budget}\n")
        out.write(f"{instance_data[instance]['ofv']}\n")

with multiprocessing.Pool(NUM_WORKERS) as pool:
    pool.map(process_file, [
        f"{nn}_{d}_{idx}.txt" for nn, d, idx in combos
    ])

print("Writing SOTA results ...")
with open(os.path.join(OUTPUT_DIR, 'sota.csv'), 'w') as f:
    f.write('instance,algorithm,gap,runtime\n')
    for instance in instance_data:
        for algo in instance_data[instance]['gaps']:
            f.write(f"{instance},{algo},{instance_data[instance]['gaps'][algo]},{instance_data[instance]['runtimes'][algo]}\n")

print("Removing raw data")
shutil.rmtree(RAW_DIR, ignore_errors=True)

print("Done.")