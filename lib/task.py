import yaml
import json
import os
import tomllib
from lib.frame import stage_frame

def stage_distribute(main_json): # input should be the whole json file
    json = main_json
    with open("../toml/task_complex.toml", "rb") as f:
        config = tomllib.load(f)
    
    stage_meta = "parsers"
    headers = list(config.keys())
    cache = []
    for _, header in enumerate(headers):
        if stage_meta in config[header]:
            new_cache, stage_json = build_json(header, config, cache)
            json['stage']['stages'].append(stage_json)
            cache = new_cache
        else: 
            continue
    return json

def check_limit(header, loaded_toml, meta, json): # meta would be the one in JOJ required json
    if "limit" not in loaded_toml[header]:
        return json
    toml_meta = ""
    match meta:
        case "cpuLimit":
            toml_meta = "cpu"
        case "memoryLimit":
            toml_meta = "mem"
        # TODO: add procLimit
        case _:
            toml_meta = meta
    
    if (toml_meta in ["stdout", "stderr"]) & (toml_meta in loaded_toml[header]['limit']):
        json['executor']['with']['default'][meta]['max'] = loaded_toml[header]['limit'][toml_meta]
        return json
    elif toml_meta in loaded_toml[header]['limit']:
        json['executor']['with']['default'][meta] = loaded_toml[header]['limit'][toml_meta]
        return json
    else:
        return json

def check_parser(header, loaded_toml, meta, json):
    return 0

def do_file_import(json, header, loaded_toml, cache):
    json['executor']['with']['default']['copyIn'] = {}
    json['executor']['with']['default']['copyInCached'] = {}
    
    # If there is no default import, we import all of the files that is in the cached
    if "files" not in loaded_toml[header]:
        json['executor']['with']['default']['copyInCached'] = {file : file for file in cache}
        return cache, json
    
    if "import" not in loaded_toml[header]['files']:
        return cache, json
    
    if loaded_toml[header]['files'] == []:
        return cache, json
    
    for _, file in enumerate(loaded_toml[header]['files']['import']):
        if file not in cache:
           json['executor']['with']['default']['copyIn'][file] = {
               "src": "home/tt/.config/joj/" + file
           }
        else:
            json['executor']['with']['default']['copyInCached'][file] = file 
    return cache, json

def do_file_export(json, header, loaded_toml, cache):
    json['executor']['with']['default']['copyOutCached'] = []
    if "files" not in loaded_toml[header]:
        return cache, json
    
    if "export" not in loaded_toml[header]['files']:
        return cache, json
    
    if loaded_toml[header]['files'] == []:
        return cache, json
    
    for _, file in enumerate(loaded_toml[header]['files']['export']):
        json['executor']['with']['default']['copyOutCached'].append(file)
        cache.append(file)
    
    return cache, json

def build_json(header, loaded_toml, cache):
    json = stage_frame()
    
    # give name to the stage
    if "name" in loaded_toml[header]:
        json['name'] = loaded_toml[header]['name']
    else:
        json['name'] = header
    
    # determine whethe its on online judge
    if "judge" in header:
        json['group'] = "joj"
    
    json['executor']['with']['default']['args'] = loaded_toml[header]['command'].split()
    
    # deal with copyIn, copyOutCached, copyInCached
    cache, json = do_file_export(json, header, loaded_toml, cache)
    cache, json = do_file_import(json, header, loaded_toml, cache)
    
    # deal with default keys limit
    limit = ["cpuLimit", "memoryLimit", "stderr", "stdout"]
    for i, meta in enumerate(limit):
        json = check_limit(header, loaded_toml, meta, json)
    
    # deal with parsers
    json['parsers'] = []
    for _, parser in enumerate(loaded_toml[header]['parsers']):
        json['parsers'].append({
            "name": parser,
            "with": {
                "score": 0,
                "comment": ""
            }
        })
        
    return cache, json
