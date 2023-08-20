import os
import sys
from glob import glob
from tqdm import tqdm
import numpy as np
import torch
import torch.nn.functional as F
import torchaudio
import laion_clap

model = laion_clap.CLAP_Module(
    enable_fusion=False, amodel='HTSAT-base')
model.load_ckpt('music_audioset_epoch_15_esc_90.14.pt')



def create_embeddings_from_text(text_data):

    audio_embed = model.text_embed = model.get_text_embedding(text_data, use_tensor=False)

    return audio_embed


def create_embeddings(audio_files):

    audio_embed = model.get_audio_embedding_from_filelist(
            x=audio_files, use_tensor=False)

    return audio_embed

