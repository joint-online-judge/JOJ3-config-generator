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
    for _, header in enumerate(headers):
        if stage_meta in config[header]:
            json['stage']['stages'].append(build_json(header, config))
            # print(header)
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

def build_json(header, loaded_toml):
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
    
    # TODO: deal with copyIn, copyOutCached, copyInCached
    
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
        
    return json
