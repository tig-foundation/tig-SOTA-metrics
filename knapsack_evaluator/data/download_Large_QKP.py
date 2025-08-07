import requests
import io
import pdfplumber
import re
import os
import numpy as np
import shutil

# Configuration
PDF_URL = "https://raw.githubusercontent.com/phil85/results-for-qkp-benchmark-instances/main/tables/Large-QKP_detailed_results.pdf"
OUTPUT_DIR = 'Large_QKP'

# Settings
n_nodes_list = [500, 1000, 2000, 5000, 10000]
densities = {500: [5, 10, 15, 20, 25, 50, 75, 100],
            1000: [5, 10, 15, 20, 25, 50],
            2000: [5, 10, 15, 20, 25],
            5000: [5, 10, 15, 20],
            10000: [5]}
budgets = ('2.5', '5.0', '10.0', '25.0', '50.0', '75.0')
SOTA_algos = ('QKBP', 'RG', 'IHEA', 'LDP', 'DP', 'QK', 'Gurobi', 'Hexaly')
combos = [(n_nodes, density)
         for n_nodes in n_nodes_list
         for density in densities[n_nodes]]

# 1) Download PDF
print("Downloading Large-QKP results PDF...")
resp = requests.get(PDF_URL)
resp.raise_for_status()

# 2) Scrape OFV data
print("Extracting Best OFV and SOTA results...")
instance_data = {}
page = 1
with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
    for nn, d in combos:
        crop = pdf.pages[page].crop((40, 145, 535, 235))
        table = crop.extract_table({
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "snap_tolerance": 3,
            "join_tolerance": 3,
        })
        assert tuple(table[0]) == (('γ', 'BestOFV') + SOTA_algos + SOTA_algos)
        assert tuple(row[0] for row in table) == (('γ', '') + budgets + ('', 'Avg', 'Min', 'Max'))
        for i, b in enumerate(budgets):
            row = table[2 + i]
            b = int(float(b) * 10)
            instance_data[f"{nn}_{d}_{b}.txt"] = {
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


# 3) Generate instances based on https://github.com/phil85/benchmark-instances-for-qkp/blob/main/generate_synthetic_instances.py
os.makedirs(OUTPUT_DIR, exist_ok=True)
# Set random seed
np.random.seed(24)

for n_nodes, density in combos:
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

    n_edges = len(edges)

    # # Write edges
    temp_file = os.path.join(OUTPUT_DIR, f'{n_nodes}_{density}.txt')
    with open(temp_file, 'w') as f:
        f.write(f'{n_nodes} {n_edges} int\n')
        for (i, j) in edges:
            f.write(f'{i} {j} {edges[(i, j)]}\n')
        # Write weights
        for weight in weights:
            f.write(f'{weight} ')
        f.write('\n')

    # Add budgets
    for b in budgets:
        b = int(float(b) * 10)
        instance = f'{n_nodes}_{density}_{b}.txt'
        shutil.copyfile(
            temp_file,
            os.path.join(OUTPUT_DIR, instance)
        )
        print(f"Writing instance {instance} ...")
        with open(os.path.join(OUTPUT_DIR, instance), 'a') as f:
            f.write(f'{int(b / 1000.0 * np.sum(weights))}\n')
            f.write(f'{instance_data[instance]['ofv']}\n')
    os.remove(temp_file)

print("Writing SOTA results ...")
with open(os.path.join(OUTPUT_DIR, 'sota.csv'), 'w') as f:
    f.write('instance,algorithm,gap,runtime\n')
    for instance in instance_data:
        for algo in instance_data[instance]['gaps']:
            f.write(f"{instance},{algo},{instance_data[instance]['gaps'][algo]},{instance_data[instance]['runtimes'][algo]}\n")

print("Done.")
