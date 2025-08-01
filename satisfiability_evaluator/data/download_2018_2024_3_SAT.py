###
# Download 3-SAT instances from the 2018-2024 SAT Competition
### 

import os
import lzma
import requests
import io

os.makedirs("2018_2024_3_SAT", exist_ok=True)
BASE_URL = "http://benchmark-database.de/file/"

for name in [
    "072785fd927ff0fd180ce8b9cc00078f",
    "0a27eb7c16c1e69ff4d087d217ac89cb",
    "0fa9521ff633b27be11525a7b0f7d8b6",
    "12b4a08e412a3bffb513ca65639c7c69",
    "12d79233413fe38d99a604487d2c3515",
    "15300be1a87777f0110722557a86bf7a",
    "24ea04bb401629158b0972463c61eed4",
    "29a5ffb47a49a6d240e08e207f320052",
    "2a5faba0239d2d40929b8ebda8c51f1e",
    "2a6bfb04f247a0790162269a5c8ec071",
    "2d0c041c0fe72dc32527bfbf34f63e61",
    "2d5cc23d8d805a0cf65141e4b4401ba4",
    "30f0db845937bbda3ffde60e5ed4cb3f",
    "3916d72a4f1795b1c624087c4e0102a1",
    "461df1a7056560279d532bc2743022b6",
    "4afd946cbaa6f41aa61dda47347dc973",
    "4eb58fc46ea3055cc3f543c73264d402",
    "5690b9b0380aa9508699e56cae5918b5",
    "5720517e098b74fdf0616d797e327a9d",
    "59fc779feee4390b57502814d424e0d6",
    "618e82c35b17ee100a3f13ca18a2e537",
    "677d10736b2d1c3a677d2301d74d731f",
    "68687b76b8bbdfc3401b9fbed2e94ffa",
    "6c63eab967a2d2aee6c73f08963fe6ba",
    "72c0d81e16d91bcaed808efcde2e5069",
    "773f3bd29e202ff700d8b5b459857a2c",
    "77b7f7bbf75faaee28f473b9941de103",
    "8117a2ac08e1acf52f660663efe2a5ca",
    "833511434f9a21861fde44bb8dbf0295",
    "a9798281fd0900a65d6f69c6978fb443",
    "b3167d999edd81291f33636464f2f8e6",
    "c2cd624b23b64a57dce567bd50b16965",
    "c4640fb558ccbad86694363a933084a5",
    "d25b135838aaa1f8e4fdb8d3a7bd9006",
    "d40a68825bdbcdd7642b249325a7b6a2",
    "d447374ab066d782661638ee4bec8a6d",
    "dba368a504f627a9fb95cf0b65b512ea",
    "e1caf89759a7dea99908ea8adb6acca4",
    "e4e212eca714fc5458e0daf485da492a",
    "e7248b57a310ad461924eb17956cdf3a",
    "eed5189b73738270ae3fdb8b33bf31c8",
    "ef16970ab9da31165d3c401ff9b29168",
    "f09f81bbbe75fc5083515ec9b586afb9",
    "f16a1da5c1f0ab9969f622a1d8dc11ac",
    "f59dd3016fb4352fe812aaf6b4dc020b",
]:
    url = f"{BASE_URL}{name}"
    print('Downloading ' + url)
    resp = requests.get(url)
    resp.raise_for_status()
    with lzma.open(io.BytesIO(resp.content), 'rb') as f:
        with open(os.path.join("2018_2024_3_SAT", name + ".cnf"), 'wb') as out:
            out.write(f.read())

print("Done")