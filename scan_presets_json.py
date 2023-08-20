
import requests, os, time, json, urllib
from collect import get_sound_infos, get_all_sound_infos

fmt = "\n=== {:30} ===\n"
latency_fmt = "latency = {:.4f}s"

BASE = "http://127.0.0.1:5000/"


#######################################
# 1. Start

print(fmt.format("SCAN HDD"))
start_time = time.time()

presets = get_all_sound_infos()
with open('presets.json', 'w') as f:
    json.dump(presets, f)

end_time = time.time()

print(fmt.format("END"))

print(latency_fmt.format(end_time - start_time))