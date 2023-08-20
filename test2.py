import requests, os, time, json
from multiprocessing.pool import ThreadPool
from time import sleep
from threading import Thread
from collect import get_sound_infos, get_all_sound_infos
import os
import sys
from glob import glob
from tqdm import tqdm
import numpy as np
import torch
import torch.nn.functional as F
import torchaudio
import laion_clap


fmt = "\n=== {:30} ===\n"
latency_fmt = "latency = {:.4f}s"

def create_embeddings(model, out_file):

    presets = []
    with open('presets.json') as f:
        presets = json.load(f)

    presets = presets[:]

    uuids = [ item['uuid'] for item in presets ]
    audio_files = [ item['preview'] for item in presets ]

    # create a thread pool
    #pool = ThreadPool(processes=10)
    print (f"{str(len(presets))} presets found in content folder(s).")

    def create (file) :
        return model.get_audio_embedding_from_filelist(x=[file], use_tensor=False)

    #for audio_file in tqdm(audio_files):

    print(fmt.format("Calc 1"))
    start_time = time.time()

    pool = ThreadPool(processes=10)
    audio_embeddings = list(pool.map(create, audio_files, chunksize=500))

    end_time = time.time()
    print(latency_fmt.format(end_time - start_time))


    np.savez_compressed(
        out_file,
        uuids=np.array(uuids),
        embeddings=audio_embeddings
    )

def main(args):

    start_time = time.time()

    """Main driver."""
    model = laion_clap.CLAP_Module(
    enable_fusion=False, amodel='HTSAT-base')
    model.load_ckpt('music_audioset_epoch_15_esc_90.14.pt')
    create_embeddings(model, args.out)

    end_time = time.time()
    print(latency_fmt.format(end_time - start_time))


if __name__ == "__main__":
    import argparse
    PARSER = argparse.ArgumentParser()

    PARSER.add_argument("out", type=str, help=\
        "Output file name")
    ARGS = PARSER.parse_args()
    main(ARGS)
