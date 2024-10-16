import sys
import tomllib
sys.path.append("../")
from lib.healthcheck import *
from lib.frame import *
from lib.compile import *
from lib.run import *

def main():    
    healthcheck_json = get_healthcheck()
    return 0

if __name__ == "__main__":
    main()

