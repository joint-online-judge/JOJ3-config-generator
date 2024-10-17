import yaml
import json
import os
import tomllib
from lib.frame import stage_frame

def stage_distribute(main_json): # input should be the whole json file
    json = main_json
    with open("../toml/task_complex.toml", "rb") as f:
        config = tomllib.load(f)
    
    stage_meta = "name"
    headers = list(config.keys())
    for _, header in enumerate(headers):
        if stage_meta in config[header]:
            json['stages'].append(build_json(header, config))
        else: 
            continue
    return json

def build_json(key, toml_file):
    json = stage_frame()
    
    return json
