
import json, os
from functools import partial


with open('misc/k_content_path.json') as path_file:
  products = json.load(path_file)

def get_preview(snd_info):
    f = snd_info['file_name']
    return os.path.dirname(f) + "/.previews/" + os.path.basename(f) + ".ogg"

def filter_func(key, id, item):
    return item[key] == id

def filter_func_list(key, id, l):
    return item[key] in l

products    = []
bank_chains = []
sound_info_mode = []
sound_info_category = []
modes = []
categories = []

with open('misc/k_content_path.json') as path_file:
  content_paths = json.load(path_file)

with open('misc/k_bank_chain.json') as path_file:
  bank_chains = json.load(path_file)

with open('misc/k_sound_info.json') as path_file:
  sound_info = json.load(path_file)

with open('misc/k_sound_info_mode.json') as path_file:
  sound_info_mode = json.load(path_file)

with open('misc/k_sound_info_category.json') as path_file:
  sound_info_category = json.load(path_file)

with open('misc/k_mode.json') as path_file:
  modes = json.load(path_file)

with open('misc/k_category.json') as path_file:
  categories = json.load(path_file)

def get_sound_infos (folder):
   
    result = []
   
    ## resolve content path
    path_list = [x for x in content_paths if x['path'] == folder]
    if len(path_list) != 1 :
       return result

    content_path = path_list[0]
    content_path_id = content_path['id']
    print ("Importing content folder: " + folder + " (ID=" + str(content_path_id) +")")

    preset_path = content_path['path'] + "/Presets"
    preview_path = preset_path + "/.previews"

    ## collect sound_infos
    list_of_snd_info = list(filter(partial(filter_func,'content_path_id', content_path_id), sound_info))

    for snd_info in list_of_snd_info:

        # bank chain
        bank_chain_id = snd_info['bank_chain_id']
        bank = list(filter(partial(filter_func, 'id', bank_chain_id), bank_chains))[0]

        # preview 
        preview = get_preview(snd_info)

        # modes
        modes_list = []
        mode_ids = list(filter(partial(filter_func, 'sound_info_id', snd_info['id']), sound_info_mode))
        for snd_md in list(filter(partial(filter_func, 'sound_info_id', snd_info['id']), sound_info_mode)) :
            mode_id = snd_md['mode_id']
            mode = list(filter(partial(filter_func, 'id', mode_id), modes))[0]
            modes_list.append(mode['name'])

        #categories
        cat_list = []
        cat_ids = list(filter(partial(filter_func, 'sound_info_id', snd_info['id']), sound_info_category))
        for snd_cat in list(filter(partial(filter_func, 'sound_info_id', snd_info['id']), sound_info_category)) :
            cat_id = snd_cat['category_id']
            cat = list(filter(partial(filter_func, 'id', cat_id), categories))[0]
            cat_list.append({'category': cat['category'],'subcategory': cat['subcategory'] })

        item = { 
            'uuid'      : snd_info['uuid'],
            'name'      : snd_info['name'],
            'file_ext'  : snd_info['file_ext'],    
            'file_name' : snd_info['file_name'], 
            'preview'   : preview,
            'upid'      : content_path['upid'],
            'vendor'    : snd_info['vendor'],
            'author'    : snd_info['author'],
            'bank1'     : bank['entry1'],      
            'bank2'     : bank['entry2'],  
            'bank3'     : bank['entry3'],
            'mode'      : modes_list,
            'category'  : cat_list,
        }
        result.append(item)
        
        if len(result) >= 5:
          break

    print (str(len(result)) + " presets imported.")
    return result



