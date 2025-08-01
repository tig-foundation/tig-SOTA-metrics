###
# Download Homberger and Gehring .txt files and matching .sol files
### 

import itertools
import requests
import os

BASE_URL = "http://vrp.galgos.inf.puc-rio.br/media/com_vrp/instances/HG/"

print('Downloading HG instances...')
os.makedirs('HG', exist_ok=True)

for combo in itertools.product(
    ['C1', 'C2', 'R1', 'R2', 'RC1', 'RC2'],
    [2, 4, 6, 8, 10],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [".txt", ".sol"]
):
    name = f"{combo[0]}_{combo[1]}_{combo[2]}{combo[3]}"
    url = f"{BASE_URL}{name}"
    print('Downloading ' + url)
    resp = requests.get(url)
    resp.raise_for_status()
    with open(os.path.join('GH', name), 'w') as f:
        f.write(resp.text)

print("Done")
