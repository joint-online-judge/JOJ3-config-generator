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
            "logPath": "" # add path of the debug log here, demand full path
        },
        "skipTeapot": False,
        "name": "",
        "stage": {
            "sandboxExecServer": "172.17.0.1:5051",
            "outputPath": "/tmp/joj3_result.json",
            "stages": []
        }
    }
    return frame