import yaml
import os
import tomllib
from lib.frame import stage_frame
from lib.diff import trans_diff

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
        if meta == "cpuLimit":
            json['executor']['with']['default'][meta] = loaded_toml[header]['limit'][toml_meta] * 1000000000
            json['executor']['with']['default']['clockLimit'] = 2 * (json['executor']['with']['default'][meta])
            return json
        elif meta == "memoryLimit":
            json['executor']['with']['default'][meta] = loaded_toml[header]['limit'][toml_meta] * 1024 * 1024           
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

def build_parser_structure(parser_list, parser, idx):
    parser_list.append({
            "name": parser,
            "with": {
                "score": 0,
                "comment": ""
            }
        })
    match parser:
        case "result-detail":
            parser_list[idx]['with']['showFiles'] = []
        case "clangtidy":
            parser_list[idx]['with']['matches'] = []
        case "keyword":
            # TODO: some of the parameters may not allow to be hardcoded
            parser_list[idx]['with']['fullscore'] = 0
            parser_list[idx]['with']['minscore'] = -30
            parser_list[idx]['with']['files'] = ["stdout"]
            parser_list[idx]['with']['forceQuitOnMatch'] = False
            
            parser_list[idx]['with']['matches'] = []
        case "cppcheck":
            parser_list[idx]['with']['matches'] = []
        case "diff":
            parser_list[idx]['with']['cases'] = []
        case "cpplint":
            return parser_list
        case "dummy":
            return parser_list
        case "result-status":
            return parser_list
    return parser_list

def check_parser(parser_list, parser, key, value, idx):
    function_list = [fix_result_detail, fix_clangtidy, fix_keyword, fix_cppcheck, fix_cpplint, fix_dummy, fix_result_status]
    for function in function_list:
        parser_list = function(parser_list, parser, key, value, idx)
    # parser_list = fix_result_detail(parser_list, parser, key, value, idx)
    # parser_list = fix_clangtidy(parser_list, parser, key, value, idx)
    # parser_list = fix_keyword(parser_list, parser, key, value, idx)
    # parser_list = fix_cppcheck(parser_list, parser, key, value, idx)
    # parser_list = fix_cpplint(parser_list, parser, key, value, idx)
    # parser_list = fix_dummy(parser_list, parser, key, value, idx)
    # parser_list = fix_result_status(parser_list, parser, key, value, idx)
    return parser_list

def fix_result_detail(parser_list, parser, key, value, idx):
    if parser != "result-detail":
        return parser_list
    if key in ["stdout", "stderr"]:
        if 'showFiles' not in parser_list[idx]['with']:
            parser_list[idx]['with']['showFiles'] = []
        show_files_list = parser_list[idx]['with']['showFiles']
    
    match key:
        case "exitstatus":
            parser_list[idx]['with']['showExitStatus'] = value
        case "mem":
            parser_list[idx]['with']['showMemory'] = value
        case "time":
            parser_list[idx]['with']['showRunTime'] = value
        case "stderr":
            if value:
                show_files_list.append("stderr")
                parser_list[idx]['with']['showFiles'] = show_files_list
        case "stdout":
            if value:
                show_files_list.append("stdout")
                parser_list[idx]['with']['showFiles'] = show_files_list
        case _:
            return parser_list

    return parser_list

def fix_clangtidy(parser_list, parser, key, value, idx):
    if parser != "clangtidy":
        return parser_list
    if not parser_list[idx]['with']['matches']:
        match_list = []
        for _, _ in enumerate(value):
            match_list.append({
                "keywords": [],
                "score": 0
            })
        parser_list[idx]['with']['matches'] = match_list
    
    match key:
        case "keyword":
            key = "matches"
            for idx_, val in enumerate(value):
                parser_list[idx]['with']['matches'][idx_]['keywords'] = [val]
        case "weight":
            key = "matches"
            for idx_, val in enumerate(value):
                parser_list[idx]['with']['matches'][idx_]['score'] = val
        case _:
            return parser_list  
    return parser_list
    
def fix_keyword(parser_list, parser, key, value, idx):
    if parser != "keyword":
        return parser_list
    
    if not parser_list[idx]['with']['matches']:
        for _, _ in enumerate(value):
            parser_list[idx]['with']['matches'].append({
                "keyword": "",
                "score": 0
            })
    
    match key:
        case "keyword":
            for idx_, val in enumerate(value):
                parser_list[idx]['with']['matches'][idx_]['keyword'] = val
        case "weight":
            for idx_, val in enumerate(value):
                parser_list[idx]['with']['matches'][idx_]['score'] = val
        case _:
            return parser_list
    
    return parser_list

def fix_cppcheck(parser_list, parser, key, value, idx):
    if parser != "cppcheck":
        return parser_list
    
    if not parser_list[idx]['with']['matches']:
        for _, _ in enumerate(value):
            parser_list[idx]['with']['matches'].append({
                "severity": [],
                "score": 0
            })
    
    match key:
        case "keyword":
            for idx_, val in enumerate(value):
                parser_list[idx]['with']['matches'][idx_]['severity'] = [val]
        case "weight":
            for idx_, val in enumerate(value):
                parser_list[idx]['with']['matches'][idx_]['score'] = val
        case _:
            return parser_list
        
    return parser_list

# TODO: to clarify the cpplint format first
# FIXME: just wait for final decision
def fix_cpplint(parser_list, parser, key, value, idx):
    if parser != "cpplint": 
        return parser_list
    
    return parser_list

def fix_dummy(parser_list, parser, key, value, idx):
    if parser != "dummy":
        return parser_list
    
    match key: 
        case "comment":
            parser_list[idx]['with']['comment'] = value    
        case _:
            return parser_list
        
    return parser_list

def fix_result_status(parser_list, parser, key, value, idx):
    if parser != "result-status":
        return parser_list
    
    match key:
        case "comment":
            parser_list[idx]['with']['comment'] = value
        case _:
            return parser_list
    
    return parser_list

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
    parser_list = []
    if "diff" in loaded_toml[header]['parsers']:
        diff_flag = True
    else:
        diff_flag = False
    
    parsers = loaded_toml[header]['parsers']
    if diff_flag:
        parsers = [parser for parser in parsers if parser != "diff"]
    
    for idx, parser in enumerate(parsers):
        parser_list = build_parser_structure(parser_list, parser, idx)
        parser_detail = loaded_toml.get(header, {}).get(parser, {})
        for key, value in parser_detail.items():
            parser_list = check_parser(parser_list, parser, key, value, idx)
    
    if diff_flag:
        parser_detail = [case for case in loaded_toml.get(header, {}) if "case" in case]
        skip_cases = []
        if "skip" in loaded_toml[header]:
            skip_cases = loaded_toml[header]['skip']
        
        (stdin_cases, diff_detail) = trans_diff(parser_detail, skip_cases, loaded_toml, header)
        diff_frame = {
            "name": "diff",
            "with": {
                "cases": []
            }
        }
        diff_frame['with']['cases'] = diff_detail
        json['executor']['with']['cases'] = stdin_cases
        parser_list.append(diff_frame)

    json['parsers'] = parser_list
    return cache, json
