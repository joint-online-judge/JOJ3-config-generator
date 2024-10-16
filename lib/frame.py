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
            "logPath": "", # add path of the debug log here, demand full path
            "skipTeapot": False,
        },
        "name": "",
        "stage": {
            "sandboxExecServer": "172.17.0.1:5051",
            "outputPath": "/tmp/joj3_result.json",
            "stages": []
        }
    }
    return frame

def get_frame():
    # TODO: may need to change the toml path.
    with open("../toml/task.toml", 'rb') as f:
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
        result_json['teapot']['logPath'] = "/home/tt/.cache/joj3/project/" + proj_name + "-debug.log"
    else:
        result_json['name'] = hw_name + " " + ex_name
        result_json['teapot']['scoreboardPath'] = "hw/" + hw_name + "-scoreboard.csv"
        result_json['teapot']['failedTablePath'] = "hw/" + hw_name + "-failed-table.md"
        result_json['teapot']['logPath'] = "/home/tt/.cache/joj3/" + hw_name + "/" + ex_name + "-debug.log"
        
    print(result_json)
    return result_json