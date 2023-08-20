import requests, os
from collect import get_sound_infos

BASE = "http://127.0.0.1:5000/"
test_url = BASE + "/upload"

#test_file = open("Ballistic.nksf.ogg", "rb") 
#test_url = "http://httpbin.org/post"

presets = get_sound_infos('/Users/Shared/Massive X Factory Library')
# presets = get_sound_infos('/Users/Shared/Monark')
# presets = get_sound_infos('/Users/Shared/Kontour')

# insert
for i in range(5):
    item = {'name': presets[i]['name'], 
            'snd_info': "info" + str(i),
            'uuid': presets[i]['uuid'],
            'upid': presets[i]['upid']
            } 

    ## put sound info
    response = requests.put(BASE + "/sounds/" + str(i), item)
    print(response.json())

    ## upload preview
    preview = presets[i]['preview']
    files = {'file': (os.path.basename(preview), open(preview, 'rb'), 'audio/ogg', {'Expires': '0'}), 'snd_info': str(presets[i])}
    response = requests.post(test_url, files = files ) 
    print(response)




#response = requests.delete(BASE + "/sounds/0")
#print(response)
#input()
#response = requests.get(BASE + "/sounds/2")
#print(response.json())