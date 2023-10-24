import os, time, json, shutil
from collect import get_sound_infos, get_all_sound_infos
from multiprocessing.pool import ThreadPool
import numpy as np
import torch
import torch.nn.functional as F
import torchaudio
import laion_clap

fmt = "\n=== {:30} ===\n"
latency_fmt = "latency = {:.4f}s"

OUTPUT_PATH = 'data'

#######################################
# 1. Start

print(fmt.format("Load Model"))

"""Main driver."""
model = laion_clap.CLAP_Module(enable_fusion=False, amodel='HTSAT-base')
model.load_ckpt('music_audioset_epoch_15_esc_90.14.pt')

print(fmt.format("SCAN HDD"))
start_time = time.time()

all_presets = get_all_sound_infos()

print(fmt.format("COPY PREVIEWS"))

_ids = []
_embeddings = []
_presets = [] 

# create folder per product
for upid, presets in all_presets.items():

    # write meta data json
    path = os.path.join(OUTPUT_PATH, upid)
    os.makedirs(path, exist_ok=True)

    ids = []
    previews = []


    for preset in presets:

        # write preview file
        dest = os.path.join(OUTPUT_PATH, upid, preset['id'] + '.ogg' )
        shutil.copyfile(preset['preview'], dest)
        preset['preview'] = dest
        ids.append(preset['id'])
        previews.append(dest)

    def create (file) :
        return model.get_audio_embedding_from_filelist(x=[file], use_tensor=False)
        
    # create a thread pool
    pool = ThreadPool(processes=10)
    audio_embeddings = list(pool.map(create, previews, chunksize=16))

    print (f"{str(len(ids))} presets found in content folder(s) - {upid}")
    
    # create embeddings
    np.savez_compressed(
        os.path.join(path,'embeddings'),
        ids=np.array(ids),
        embeddings=audio_embeddings
    )

    # create json
    with open(os.path.join(path,'presets.json'), 'w') as f:
        json.dump(presets, f)

    _presets += presets
    _ids += ids
    _embeddings += audio_embeddings

# create embeddings
np.savez_compressed(
    os.path.join(OUTPUT_PATH,'embeddings'),
    ids=np.array(_ids),    
    embeddings=_embeddings
)

 # create json
with open(os.path.join(OUTPUT_PATH,'presets.json'), 'w') as f:
    json.dump(_presets, f)

end_time = time.time()

print(fmt.format("END"))

print(latency_fmt.format(end_time - start_time))