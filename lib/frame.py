import tomllib
import json
import yaml
import os

def main_frame():
    frame = {
        "teapot": {
            "scoreboardPath": "",
            "failedTablePath": "",
            "gradingRepoName": "engr151-joj",
            "logPath": "", # add path of the teapot debug log here, demand full path
            "skipTeapot": False,
        },
        "logPath": "",
        "name": "",
        "stage": {
            "sandboxExecServer": "172.17.0.1:5051",
            "outputPath": "/tmp/joj3_result.json",
            "stages": []
        }
    }
    return frame

def stage_frame():
    json = {
        "name": "",
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
                "copyIn": {}, # TODO: may need to modify in future for this "copyIn"
                "copyInCached": [],
                "copyOutCached": [],
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
      "parsers": []
    }
    return json

def get_frame():
    # TODO: may need to change the toml path.
    with open("../toml/task_simple.toml", 'rb') as f:
        config = tomllib.load(f)
    
    result_json = main_frame()
    
    task_name = config['task']
    hw_name = ""
    ex_name = ""
    proj_name = ""
    if len(task_name.split()) != 1:
        hw_name = task_name.split()[0]
        ex_name = task_name.split()[1]
    else:
        proj_name = task_name
    
    if not len(proj_name) == 0:
        result_json['name'] = proj_name
        result_json['teapot']['scoreboardPath'] = "project/" + proj_name + "-scoreboard.csv"
        result_json['teapot']['failedTablePath'] = "project/" + proj_name + "-failed-table.md"
        result_json['teapot']['logPath'] = "/home/tt/.cache/joj3/project/" + proj_name + "-teapot-debug.log"
        result_json['logPath'] = "/home/tt/.cache/joj3/project/" + proj_name + "-debug.log"
    else:
        result_json['name'] = hw_name + " " + ex_name
        result_json['teapot']['scoreboardPath'] = "hw/" + hw_name + "-scoreboard.csv"
        result_json['teapot']['failedTablePath'] = "hw/" + hw_name + "-failed-table.md"
        result_json['teapot']['logPath'] = "/home/tt/.cache/joj3/" + hw_name + "/" + ex_name + "-teapot-debug.log"
        result_json['logPath'] = "/home/tt/.cache/joj3/" + hw_name + "/" + ex_name + "-debug.log"
    
    result_json['stage']['stages'] = []
    return result_json