import sys
import tomllib
import json
import os
sys.path.append("../")
from lib.repo import *
from lib.frame import *
from lib.task import *
from lib.distribute import *

def main():    
    repo_json = get_healthcheck()
    frame = get_frame()
    frame['stage']['stages'].append(repo_json)
    frame = stage_distribute(frame)
    # print(frame)
    with open("../outputs/sample.json", "w") as f:
        json.dump(frame, f, indent=4)
    return frame

if __name__ == "__main__":
    main()
