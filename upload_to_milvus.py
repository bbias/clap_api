from milvus_db import clap_db, snd_info_db, search_milvus_db, insert_items 
import numpy as np
import json

fmt = "\n=== {:30} ===\n"
latency_fmt = "latency = {:.4f}s"
search_latency_fmt = "search latency = {:.4f}s"
DIM = 512

def upload_embeddings():
    


    presets = []
    with open('presets.json') as f:
        presets = json.load(f)

    print(fmt.format("Load Embeddings"))

    embeddings_file = np.load('ALL_PRESETS_WITH_UUID_31926.npz')

    print(fmt.format("Load Embeddings"))


