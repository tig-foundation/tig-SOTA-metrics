
###
# Download Solomon .txt files and matching .sol files
### 

import requests
import os

BASE_URL = "http://vrp.galgos.inf.puc-rio.br/media/com_vrp/instances/Solomon/"

print('Downloading Solomon instances...')
os.makedirs('Solomon', exist_ok=True)

for prefix, num_instances in [
    ('C1', 9),
    ('C2', 8),
    ('R1', 12),
    ('R2', 11),
    ('RC1', 8),
    ('RC2', 8),
]:
    for n in range(1, num_instances + 1):
        for ext in ['.txt', '.sol']:
            name = f"{prefix}{n:02d}{ext}"
            url = f"{BASE_URL}{name}"
            print('Downloading ' + url)
            resp = requests.get(url)
            resp.raise_for_status()
            with open(os.path.join('Solomon', name), 'w') as f:
                f.write(resp.text)

print("Done")