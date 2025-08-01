###
# Download Homberger and Gehring .txt files and matching .sol files
### 

import concurrent.futures
import time
import itertools
import requests
import os

if not os.path.exists('GH'):
    os.makedirs('GH')

MAX_WORKERS = 8
BASE_URL = "http://vrp.galgos.inf.puc-rio.br/media/com_vrp/instances/HG/"

def download_instance(download_url, save_path):
    for i in range(3):
        try:
            print('Downloading ' + download_url)
            resp = requests.get(download_url)
            resp.raise_for_status()
            with open(save_path, 'w') as f:
                f.write(resp.text)
            break
        except Exception as e:
            print(f"Error downloading {download_url}: {e}")
            print(f"Retrying {download_url}: {i+1} of 3")
            time.sleep(i * 2)

tasks = []
for combo in itertools.product(
    ['C1', 'C2', 'R1', 'R2', 'RC1', 'RC2'],
    [2, 4, 6, 8, 10],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [".txt", ".sol"]
):
    name = f"{combo[0]}_{combo[1]}_{combo[2]}{combo[3]}"
    url = f"{BASE_URL}{name}"
    save_path = os.path.join('GH', name)
    tasks.append((url, save_path))

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(download_instance, url, save_path) for url, save_path in tasks]
    for future in concurrent.futures.as_completed(futures):
        pass

print("Done.")
