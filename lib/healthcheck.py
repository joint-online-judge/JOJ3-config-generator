import tomllib
import json
import yaml
import os

def healthcheck_frame():
    healthcheck_json = {
        "name": "healthcheck",
        "executor": {
        "name": "sandbox",
        "with": {
          "default": {
            "args": [], # main input should be on the args side
            "env": [
              "PATH=/usr/bin:/bin:/usr/local/bin"
            ],
            "cpuLimit": 10000000000, # almost immutable for the following three fields
            "memoryLimit": 104857600, 
            "procLimit": 50,
            "copyInDir": ".",
            "copyIn": {
                "/tmp/repo-health-checker": {
                    "src": "/usr/local/bin/repo-health-checker"
                }
            }, # TODO: may need to modify in future for this "copyIn"
            "copyOut":[
                "stdout",
                "stderr"
            ],
            "stdin": {
              "content": ""
            },
            "stdout": {
              "name": "stdout",
              "max": 65536
            }, # bugs may occur that stdout is not large enough
            "stderr": {
              "name": "stderr",
              "max": 65536
            }
          }
        }
      },
      "parsers": [
        {
        "name": "result-status",
        "with": {
          "score": 0,
          "comment": "" # leave the comment empty so that we can hide this stage in the issue that teapot sent
        }
      }
    ]
    }
    return healthcheck_json

def fill_healthcheck(): 
  with open("../toml/repo.toml", 'rb') as f:
    config = tomllib.load(f)
    
  json = healthcheck_frame()

  teaching_team = config['teaching_team']
  repoSize = config['max_size']
  release_tags = config['release_tags']
  immutable = config['files']['immutable']
  required_files = config['files']['required']
  whitelist = config['files']['whitelist']['patterns']

  # process reposize
  repoSize = "-repoSize=" + str(repoSize) + " "
  
  # process release tags
  for i, tag in enumerate(release_tags):
    release_tags[i] = "-releaseTag=" + tag + " "
  
  # process required files
  # TODO: check whether the meta flag is valid
  for i, meta in enumerate(required_files):
    required_files[i] = "-meta=" + meta + " "
  
  # process white list
  for i, file in enumerate(whitelist):
    whitelist[i] = "-whitelist=" + file + " "
  
  # process immutable file
  immutable_files = "-checkFileNameList="
  for i, name in enumerate(immutable):
    if i == len(immutable) - 1:
      immutable_files = immutable_files + name + " "
    else:
      immutable_files = immutable_files + name + ","
  print(immutable_files)
  
  return 0

