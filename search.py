import sys
import numpy as np
import laion_clap
import json
import os.path
import argparse
parser = argparse.ArgumentParser()

count = 5


## load embedding
embeddings_file = 'NEW.npz'
data = np.load(embeddings_file)

## load model
model = laion_clap.CLAP_Module(
    enable_fusion=False, amodel='HTSAT-base')
model.load_ckpt('music_audioset_epoch_15_esc_90.14.pt')

def search_by_id(search_id):
    result = []
    idd = 0

    # get element with search_id
    for fn, audio_embed in  zip(data['filenames'],data['embeddings']) :

        if idd == search_id:

            cos_sim = np.dot(audio_embed, data['embeddings'].T)
            cos_sim_pct_hit = 100*(cos_sim+1)/2
            sim_scores = cos_sim_pct_hit

            idx_sort = np.argsort(-sim_scores)[1:count]
            scores_sorted = sim_scores[idx_sort]

            rel_ids = '[ '
            sim = [] 

            for m, score in zip(idx_sort, scores_sorted):

                if score < 90.0 :
                    break

                sim.append({"id": m , "sc" : int(score * 10.0) })
                ##print(f"{m} - {name}: {score}")
                rel_ids = rel_ids + ("%d," % (m))

            rel_ids = rel_ids[:-1] + ']'

            head, tail = os.path.split(fn)

            item = {"id": idd , 
                    "filename": fn,
                    "foldername" : head, 
                    "basename" : tail,
                    "related_ids" : rel_ids,
                    "sim" : sim
                    }
            result.append(item)

            return json.dumps(result, default=convert)

        idd = idd + 1

    return "{Error}"
""""
        with open("data_file.json", "w") as write_file:
            json.dump(result, write_file, default=convert)
"""


def convert(o):
    if isinstance(o, np.generic): return o.item()  
    raise TypeError






