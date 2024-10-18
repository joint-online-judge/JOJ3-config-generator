import sys
import tomllib
sys.path.append("../")
from lib.repo import *
from lib.frame import *
from lib.task import *

def main():    
    repo_json = get_healthcheck()
    frame = get_frame()
    frame['stage']['stages'].append(repo_json)
    frame = stage_distribute(frame)
    print(frame)
    return frame

if __name__ == "__main__":
    main()

