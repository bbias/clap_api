from milvus_db import clap_db, search_milvus_db, insert_items 
import numpy as np
import json, os

fmt = "\n=== {:30} ===\n"
latency_fmt = "latency = {:.4f}s"
search_latency_fmt = "search latency = {:.4f}s"
DIM = 512

OUTPUT_PATH = 'data_5K'

def upload_embeddings():
    
    print(fmt.format("Load Presets"))

    presets = []
    with open(os.path.join(OUTPUT_PATH,'presets.json')) as f:
        presets = json.load(f)
    print("Num presets loaded: " + str(len(presets)))

    # load embeddings
    print(fmt.format("Load Embeddings"))
    embeddings_file = np.load(os.path.join(OUTPUT_PATH,'embeddings.npz'))
    ids = embeddings_file['ids']
    embeddings = embeddings_file['embeddings']

    # flatten embeddings
    embeddings = [sub[0] for sub in embeddings]

    print("Num embeddings loaded: " + str(len(embeddings)))


    print(fmt.format("Create Entries for Milvus"))
    
    # entities = []
    #for preset, id, emb in zip(presets, embeddings_file['ids'], embeddings_file['embeddings']):

    upids       = [sub['upid'] for sub in presets]
    alias       = [sub['alias'] for sub in presets]
    names       = [sub['name'] for sub in presets]
    previews    = [sub['preview'] for sub in presets]
    vendor      = [sub['vendor'] for sub in presets]
    bank1       = [sub['bank1'] for sub in presets]
    bank2       = [sub['bank2'] for sub in presets]
    cat         = [sub['category'] for sub in presets]
    mod         = [sub['mode'] for sub in presets]

    mode = list()
    category  = list()
    sub_category  = list()
    for sub in cat:
        if len(sub) >0 :
            sub_category.append(sub[0]['subcategory'])
            category.append(sub[0]['category'])
        else:
            sub_category.append("")
            category.append("")

    for sub in mod:
        mode.append(",".join(sub)) 
    

    # remove None values
    vendor = ['' if v is None else v for v in vendor]
    bank1 = ['' if v is None else v for v in bank1]
    bank2 = ['' if v is None else v for v in bank2]
    category = ['' if v is None else v for v in category]
    sub_category = ['' if v is None else v for v in sub_category]
    mode = ['' if v is None else v for v in mode]

    chunks_size = 8192
    num_items   = len(upids)
    idx = 0

    while num_items:

        n = min(chunks_size, num_items)

        entities    = [ids[idx:idx+n], 
                       upids[idx:idx+n], 
                       alias[idx:idx+n], 
                       names[idx:idx+n], 
                       previews[idx:idx+n], 
                       vendor[idx:idx+n], 
                       bank1[idx:idx+n], 
                       bank2[idx:idx+n], 
                       category[idx:idx+n], 
                       sub_category[idx:idx+n], 
                       mode[idx:idx+n], 
                       embeddings[idx:idx+n]]
        
        insert_result = clap_db.insert(entities)
        print(insert_result)

        idx += n
        num_items -= n

upload_embeddings()

 