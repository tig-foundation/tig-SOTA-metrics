import io
import requests
import zipfile
import os
import patoolib
import pdfplumber
import re
import shutil
import multiprocessing

if not shutil.which('unrar'):
    raise RuntimeError("You need to have 'unrar' installed to extract RAR files.")

# --- Configuration ---
PDF_URL = "https://raw.githubusercontent.com/phil85/results-for-qkp-benchmark-instances/main/tables/QKPGroupII_detailed_results.pdf"
ZIP_URL = "https://leria-info.univ-angers.fr/~jinkao.hao/QKPDATA/QKPGroupII.zip"
OUTPUT_DIR = 'QKPGroupII'
RAW_DIR = os.path.join(OUTPUT_DIR, 'raw_data')
NUM_WORKERS = 8

n_nodes_list = [1000, 2000]
densities = {
    1000: sorted(map(str, [25, 50, 75, 100])),
    2000: sorted(map(str, [25, 50, 75, 100])),
}
n_instances = 10
combos = [(n_nodes, density, idx)
         for n_nodes in n_nodes_list
         for density in densities[n_nodes]
         for idx in sorted(map(str, range(1, n_instances + 1)))]
SOTA_algos = ('QKBP', 'RG', 'IHEA', 'LDP', 'DP', 'QK', 'Gurobi', 'Hexaly')

# 1) Download & parse the PDF
print("Downloading Group II detailed results PDF...")
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
        
print(f"Extracted data for {len(instance_data)} instances.")

# 2) Prepare directories
os.makedirs(RAW_DIR, exist_ok=True)

# 3) Download & unzip the raw data ZIP into memory
print("Downloading raw Group II zip...")
resp = requests.get(ZIP_URL)
resp.raise_for_status()

print("Extracting raw Group II data...")
with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
    zf.extractall(RAW_DIR)

# 4) Extract each .rar archive in RAW_DIR (minimal disk I/O)
for prefix in ['1000', '2000']:
    if prefix == '1000':
        dens_list = [25, 50, 75, 100]
    else:
        dens_list = ['25', '50(1)', '50(2)', '75(1)', '75(2)', '100(1)', '100(2)']
    for d in dens_list:
        rar_name = f"{prefix}_{d}.rar"
        rar_path = os.path.join(RAW_DIR, "QKPGroupII", rar_name)
        # Extract RAR to RAW_DIR using temporary files
        patoolib.extract_archive(rar_path, outdir=RAW_DIR)
        # Move contents up one level
        folder = os.path.join(RAW_DIR, f"{prefix}_{d}")
        if os.path.isdir(folder):
            for f_name in os.listdir(folder):
                os.replace(os.path.join(folder, f_name), os.path.join(RAW_DIR, f_name))

# 5) Process .dat files into .txt files with OFV appended
print("Processing .dat files into .txt format...")

def process_dat_file(instance):
    print(f"Processing {instance}")
    lines = open(os.path.join(RAW_DIR, instance.replace('.txt', '.dat')), 'r').read().splitlines()
    nn = int(lines[0].strip())

    edges = []
    linear = [int(v) for v in lines[1].split() if v]
    for i in range(nn):
        edges.append((i, i, linear[i]))
    for i in range(nn):
        quad = [int(v) for v in lines[2 + i].split() if v]
        for j in range(i + 1, nn):
            val = quad[j - (i + 1)]
            if val != 0:
                edges.append((i, j, val))

    budget = int(lines[3 + nn].strip())
    weights = [int(v) for v in lines[4 + nn].split() if v]

    with open(os.path.join(OUTPUT_DIR, instance), 'w') as out:
        out.write(f"{nn} {len(edges)} int\n")
        for i, j, val in edges:
            out.write(f"{i} {j} {val:.6f}\n")
        out.write(" ".join(str(w) for w in weights) + "\n")
        out.write(f"{budget}\n")
        out.write(f"{instance_data[instance]['ofv']}\n")

with multiprocessing.Pool(NUM_WORKERS) as pool:
    pool.map(process_dat_file, [
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