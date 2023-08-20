import json, os
from glob import glob

presets = []
with open('presets.json') as f:
    presets = json.load(f)

#presets = presets[:1000]

uuids       = list(sub['id'] for sub in presets)
filenames   = list(sub['file_name'] for sub in presets)

import collections
doublicates = [item for item, count in collections.Counter(uuids).items() if count > 1]

result = []

for u, f in zip (uuids, filenames):
    if u in doublicates:
        result.append({u,f})

print (result)
print ("Num doublicates: " + str(len(doublicates)))