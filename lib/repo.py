import tomllib
import json
import yaml
import os
import hashlib
from lib.frame import stage_frame

def calc_sha256sum(file_path):
  sha256_hash = hashlib.sha256()
  with open(file_path, "rb") as f:
    for byte_block in iter(lambda: f.read(65536*2), b""):
      sha256_hash.update(byte_block)
  return sha256_hash.hexdigest()

def healthcheck_frame():
  json = stage_frame()
  json['name'] = "healthcheck"
  json['executor']['with']['default']['copyIn'] = {
    "tmp/repo-health-checker":{
      "src": "/usr/local/bin/repo-health-checker"
    }
  }
  json['parsers'].append({
    "name": "healthcheck",
    "with": {
      "score": 0,
      "comment": "" # leave the comment empty to hide this stage on teapot
    }
  })
  return json

def get_hash(immutable_files): # input should be a list
  file_path = "../immutable_file/" # TODO: change this when things are on the server
  immutable_hash = []
  for i, file in enumerate(immutable_files):
    immutable_files[i] = file_path + file.rsplit('/', 1)[-1]
  
  for i, file in enumerate(immutable_files):
    immutable_hash.append(calc_sha256sum(file))
  
  hash_check = "-checkFileSumList="
  
  for i, file in enumerate(immutable_hash):
    if i == len(immutable_hash) - 1:
      hash_check = hash_check + file + " "
    else: 
      hash_check = hash_check + file + ","
  return hash_check

def get_healthcheck(): 
  # TODO: may need to change the toml path.
  with open("../toml/repo.toml", 'rb') as f:
    config = tomllib.load(f)
    
  result_json = healthcheck_frame()

  teaching_team = config['teaching_team']
  # check_release = config['check_release']
  repoSize = config['maxsize']
  release_tags = config['releasetags']
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
  
  # add chore and necessary args
  chore = "/tmp/repo-health-checker -root=.  "
  
  # TODO: add whether check release situation
  # check_release_ = "checkRelease=" + check_release + " "
  # concatenate
  args = ""
  args = args + chore
  args = args + repoSize
  # args = args + check_release_
  for _, meta in enumerate(release_tags):
    args = args + meta
  
  for _, meta in enumerate(required_files):
    args = args + meta
  
  for _, meta in enumerate(whitelist):
    args = args + meta
  
  args = args + get_hash(immutable)
  print(get_hash(immutable))
  
  args = args + immutable_files
  result_json["executor"]["with"]["args"] = args.split()
  
  # TODO: remove this debug print
  print(result_json["executor"]["with"]["args"])
  return result_json