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
OUT_DIR = 'QKPGroupII'
RAW_DIR = os.path.join(OUT_DIR, 'raw_data')
NUM_WORKERS = 8

# 1) Download & parse the PDF
print("Downloading Group II detailed results PDF...")
resp = requests.get(PDF_URL)
resp.raise_for_status()

print("Extracting Best OFV values for Group II...")
ofv_map = {}
with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
    for i, page in enumerate(pdf.pages):
        if i == 0:
            continue  # Skip the first page as it contains no instance data
        
        lines = (page.extract_text() or "").split("\n")
        # e.g. "File 1000 25 1.txt"
        inst_line = next((l for l in lines if l.startswith("File ")))

        raw_name = inst_line.replace("File ", "").strip()
        # locate the γ header line
        header_idx = next((i for i, l in enumerate(lines) if l.startswith("γ ")))

        tokens = lines[header_idx + 1].split()

        # parse OFV, remove commas, then to int
        ofv_val = int(float(tokens[1].replace(",", "")))
        # normalize "1000 25 1.txt" → "1000_25_1.txt"
        m = re.match(r"(\d+)\s+(\d+)\s+(\d+)\.txt", raw_name)
        n, d, idx = m.groups()
        key = f"{n}_{int(d)}_{int(idx)}.txt"
        ofv_map[key] = ofv_val
        
print(f"Mapped OFV for {len(ofv_map)} instances")

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
n_nodes_list = [1000, 2000]
densities = {1000: [25, 50, 75, 100], 2000: [25, 50, 75, 100]}

def process_dat_file(name):
    print(f"Processing {name}")
    lines = open(os.path.join(RAW_DIR, f"{name}.dat"), 'r').read().splitlines()
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

    txt_name = f"{name}.txt"
    with open(os.path.join(OUT_DIR, txt_name), 'w') as out:
        out.write(f"{nn} {len(edges)} int\n")
        for i, j, val in edges:
            out.write(f"{i} {j} {val:.6f}\n")
        out.write(" ".join(str(w) for w in weights) + "\n")
        out.write(f"{budget}\n")
        out.write(f"{ofv_map[txt_name]}\n")

tasks = []
for n_nodes in n_nodes_list:
    for density in densities[n_nodes]:
        for instance in range(1, 11):
            tasks.append(f"{n_nodes}_{density}_{instance}")

with multiprocessing.Pool(NUM_WORKERS) as pool:
    pool.map(process_dat_file, tasks)

print("Removing raw data")
shutil.rmtree(RAW_DIR, ignore_errors=True)

print("Done.")