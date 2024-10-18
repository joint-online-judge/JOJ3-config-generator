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

def build_parser_structure(json, parser, idx):
    json['parsers'].append({
            "name": parser,
            "with": {
                "score": 0,
                "comment": ""
            }
        })
    match parser:
        case "result-detail":
            json['parsers'][idx]['with']['showFiles'] = []
        case "clangtidy":
            json['parsers'][idx]['with']['matches'] = []
        case "keyword":
            # TODO: some of the parameters may not allow to be hardcoded
            json['parsers'][idx]['with']['fullscore'] = 0
            json['parsers'][idx]['with']['minscore'] = -30
            json['parsers'][idx]['with']['files'] = ["stdout"]
            json['parsers'][idx]['with']['forceQuitOnMatch'] = False
            
            json['parsers'][idx]['with']['matches'] = []
        case "cppcheck":
            json['parsers'][idx]['with']['matches'] = []
        case "diff":
            json['parsers'][idx]['with']['cases'] = []
        case "cpplint":
            return json
        case "dummy":
            return json
        case "result-status":
            return json
    return json

def check_parser(json, parser, key, value, idx):
    return 0

def fix_result_detail(json, parser, key, value, idx):
    if parser != "result-detail":
        return json
    
    match key:
        case "exitstatus":
            key = "showExitStatus"
            json['parsers'][idx]['with'][key] = value
        case "mem":
            key = "showMemory"
            json['parsers'][idx]['with'][key] = value
        case "time":
            key = "showRunTime"
            json['parsers'][idx]['with'][key] = value
        case "stderr":
            key = "showFiles"
            if value:
                json['parsers'][idx]['with'][key].append("stderr")
        case "stdout":
            key = "showFiles"
            if value:
                json['parsers'][idx]['with'][key].append("stdout")
        case _:
            return json
    return json

def fix_clangtidy(json, parser, key, value, idx):
    if parser != "clangtidy":
        return key, value
    if not json['parsers'][idx]['with']['matches']:
        for _, _ in enumerate(value):
            json['parsers'][idx]['with']['matches'].append({
                "keywords": [],
                "score": 0
            })
    match key:
        case "keyword":
            key = "matches"
            for idx_, val in enumerate(value):
                json['parsers'][idx]['with']['matches'][idx_]['keywords'] = [val]
        case "weight":
            key = "matches"
            for idx_, val in enumerate(value):
                json['parsers'][idx]['with']['matches'][idx_]['score'] = val
        case _:
            return json  
    return json
    
def fix_keyword(json, parser, key, value, idx):
    if parser != "keyword":
        return json
    
    if not json['parsers'][idx]['with']['matches']:
        for _, _ in enumerate(value):
            json['parsers'][idx]['with']['matches'].append({
                "keyword": "",
                "score": 0
            })
    
    match key:
        case "keyword":
            for idx_, val in enumerate(value):
                json['parsers'][idx]['with']['matches'][idx_]['keyword'] = val
        case "weight":
            for idx_, val in enumerate(value):
                json['parsers'][idx]['with']['matches'][idx_]['score'] = val
        case _:
            return json
    
    return json

def fix_cppcheck(json, parser, key, value, idx):
    if parser != "cppcheck":
        return json
    
    if not json['parsers'][idx]['with']['matches']:
        for _, _ in enumerate(value):
            json['parsers'][idx]['with']['matches'].append({
                "severity": [],
                "score": 0
            })
    
    match key:
        case "keyword":
            for idx_, val in enumerate(value):
                json['parsers'][idx]['with']['matches'][idx_]['severity'] = [val]
        case "weight":
            for idx_, val in enumerate(value):
                json['parsers'][idx]['with']['matches'][idx_]['score'] = val
        case _:
            return json
        
    return json

# TODO: fix the diff parser format as well as the stdin part
def fix_diff(json, parser, key, value, idx):
    if parser != "diff":
        return json

    if not json['parsers'][idx]['with']['cases']:
        for _, _ in enumerate(value):
            json['parsers'][idx]['with']['cases'].append({
                "outputs": [
                    {
                        
                    }
                ]
            })

# TODO: to clarify the cpplint format first
def fix_cpplint(json, parser, key, value, idx):
    if parser != "cpplint": 
        return json
    
    return json

def fix_dummy(json, parser, key, value, idx):
    if parser != "dummy":
        return json
    
    match key: 
        case "comment":
            json['parsers'][idx]['with']['comment'] = value    
        case _:
            return json
        
    return json

def fix_result_status(json, parser, key, value, idx):
    if parser != "result-status":
        return json
    
    match key:
        case "comment":
            json['parsers'][idx]['with']['comment'] = value
        case _:
            return json
    
    return json

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
    for idx, parser in enumerate(loaded_toml[header]['parsers']):
        json = build_parser_structure(json, parser, idx)
        parser_detail = loaded_toml.get(header, {}).get(parser, {})
        for key, value in parser_detail.items():
            json['parsers'][idx]['with'][key] = value
    
    return cache, json
