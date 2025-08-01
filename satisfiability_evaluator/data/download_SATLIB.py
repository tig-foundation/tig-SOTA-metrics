###
# Download uniform random 3-SAT instances from SATLIB
###

import os
import io
import tarfile
import requests

os.makedirs("SATLIB", exist_ok=True)
BASE_URL = "https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/"

for dataset in [
    "uf20-91",
    "uf50-218",
    "uf75-325",
    "uf100-430",
    "uf125-538",
    "uf150-645",
    "uf175-753",
    "uf200-860",
    "uf225-960",
    "uf250-1065",
]:
    url = f"{BASE_URL}{dataset}.tar.gz"
    print(f"Downloading {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    with tarfile.open(fileobj=io.BytesIO(resp.content), mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.endswith('.cnf'):
                continue                
            with tar.extractfile(member) as f:
                with open(os.path.join("SATLIB", os.path.basename(member.name)), 'wb') as out:
                    out.write(f.read())

print("Done")