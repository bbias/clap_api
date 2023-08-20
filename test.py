import requests, os, time, json, urllib
from collect import get_sound_infos, get_all_sound_infos

fmt = "\n=== {:30} ===\n"
latency_fmt = "latency = {:.4f}s"

BASE = "http://127.0.0.1:5000/"


#######################################
# 1. Start

print(fmt.format("SCAN HDD"))
start_time = time.time()

#presets = get_all_sound_infos()
#with open('presets.json', 'w') as f:
#    json.dump(presets, f)

presets = []
with open('presets.json') as f:
    presets = json.load(f)

#presets = presets[:1000]

print (f"{str(len(presets))} presets found in content folder(s).")

print(fmt.format("IMPORT"))

files = [ item['preview'] for item in presets ]

#### chunk 
num_entities = len(presets)
idx = 0
counter = 0

while num_entities > 0:
    num = min(num_entities, 1024)

    files = []
    for i in range(num):
        preset = presets[idx + i]

        counter += 1

        """
        ### create sound info
        item = {'basename': preset['basename'], 
            'snd_info': "info" + str(i),
            'uuid': preset['uuid'],
            'upid': preset['upid']
        }
        response = requests.post(BASE + "/sound_info", json=item, timeout=120)
        """
        ### upload preview
        preview = preset['preview']
        files.append((preset['id'], (urllib.parse.quote(preset['upid'] + "/" + os.path.basename(preview)), open(preview, 'rb'), 'audio/ogg')))

    response = requests.post(BASE + "/upload", files = files, timeout=120 ) 

    if (response.status_code != 201):
        print("")

    num_entities -= num
    idx += num
    print(idx)


end_time = time.time()

print(fmt.format("End"))
print(latency_fmt.format(end_time - start_time))

print(fmt.format("END"))
