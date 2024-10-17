import sys
import tomllib
sys.path.append("../")
from lib.repo import *
from lib.frame import *
from lib.compile import *
from lib.task import *

def main():    
    healthcheck_json = get_healthcheck()
    frame = get_frame()
    return 0

if __name__ == "__main__":
    main()

