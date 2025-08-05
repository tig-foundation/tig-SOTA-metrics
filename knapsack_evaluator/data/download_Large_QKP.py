import requests
import io
import pdfplumber
import re
import os
import numpy as np

# Configuration
PDF_URL = "https://raw.githubusercontent.com/phil85/results-for-qkp-benchmark-instances/main/tables/Large-QKP_detailed_results.pdf"
OUT_DIR = 'Large_QKP'

# 1) Download PDF
print("Downloading Large-QKP results PDF...")
resp = requests.get(PDF_URL)
resp.raise_for_status()

# 2) Scrape OFV data
print("Scraping Best OFV values for all instances...")
ofv_map = {}
with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
    for i, page in enumerate(pdf.pages):
        if i == 0:
            continue  # Skip the first page as it contains no instance data
        lines = (page.extract_text() or "").split("\n")
        # Find the instance descriptor line
        inst_line = next((l for l in lines if l.lower().startswith("file qkp new")), None)
        # Parse "File qkp new 00500 005 0.txt"
        m = re.match(
            r"File\s+qkp new\s+0*(\d+)\s+0*(\d+)\s+(\d+)\.txt",
            inst_line, re.IGNORECASE
        )
        n_nodes, density, seed = m.groups()
        # Locate the γ header line
        header_idx = next((i for i, l in enumerate(lines) if l.startswith("γ ")), None)
        # Next six lines correspond to the six budgets (γ settings)
        for offset in range(1, 7):
            parts = lines[header_idx + offset].split()
            budget = int(float(parts[0]) * 10)
            ofv = int(float(parts[1].replace(",", "")))
            instance = f"large_qkp_{int(n_nodes)}_{int(density)}_{int(seed)}_{budget}.txt"
            ofv_map[instance] = ofv

print(f"Mapped OFV for {len(ofv_map)} instances.")


# 3) Generate instances based on https://github.com/phil85/benchmark-instances-for-qkp/blob/main/generate_synthetic_instances.py
os.makedirs(OUT_DIR, exist_ok=True)
n_nodes_list = [500, 1000, 2000, 5000, 10000]
densities = {500: [5, 10, 15, 20, 25, 50, 75, 100],
            1000: [5, 10, 15, 20, 25, 50],
            2000: [5, 10, 15, 20, 25],
            5000: [5, 10, 15, 20],
            10000: [5]}
budgets = [25, 50, 100, 250, 500, 750]

# Set random seed
np.random.seed(24)

for n_nodes in n_nodes_list:
    for density in densities[n_nodes]:
        # Randomly draw linear and quadratic coefficients in [1, 100]
        utility_matrix = np.random.randint(1, 101, size=(n_nodes, n_nodes))
        utility_matrix = np.tril(utility_matrix) + np.tril(utility_matrix, -1).T

        # Apply density
        utility_matrix = utility_matrix * (np.random.rand(n_nodes, n_nodes) < (density / 100))

        edges = {}
        for i in range(n_nodes):
            for j in range(i, n_nodes):
                if utility_matrix[i, j] > 0:
                    edges[i, j] = utility_matrix[i, j]

        # Randomly draw weights in [1, 50]
        weights = np.random.randint(1, 51, size=n_nodes)

        instance = ""
        n_edges = len(edges)
        instance += f'{n_nodes} {n_edges} float\n'

        # Write edges
        for (i, j) in edges:
            instance += f'{i} {j} {edges[(i, j)]:.6f}\n'

        # Write weights
        for weight in weights:
            instance += f'{weight} '
        instance += '\n'

        # Add budgets
        for b in budgets:
            instance_name = f'large_qkp_{n_nodes}_{density}_{seed}_{b}.txt'
            print(f"Writing instance {instance_name} ...")
            with open(os.path.join(OUT_DIR, instance_name), 'w') as f:
                f.write(
                    instance + 
                    f'{int(b / 1000.0 * np.sum(weights))}\n' +
                    f'{ofv_map[instance_name]}\n'
                )

print("Done.")