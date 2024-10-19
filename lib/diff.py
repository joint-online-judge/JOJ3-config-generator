import tomllib
import json
import os
import yaml

def ex2e(strin):
    alphabet = list(strin)
    result = alphabet[0] + alphabet[2]
    return result

def get_name():
    # TODO: may need to change the toml path.
    with open("../toml/task_complex.toml", 'rb') as f:
        config = tomllib.load(f)
    
    task_name = config['task']
    
    return task_name.split()[0], task_name.split()[1]

# TODO: fix the diff parser format as well as the stdin part
# FIXME: feels fix_diff would have different input
def trans_diff(parser_detail, skip_cases, loaded_toml, header): 
    '''
    - stdin_cases would be a list store all the detail of the input cases
    - parser_detail would store the cases that needs special care (cpu, mem, etc.)
    - skip cases would store the cases that would be asked to skip
    - loaded_toml would store the data of the original toml file
    '''
    stdin_cases = []
    diff_detail = []
    outername, innername = get_name()
    # Now get default testcases situation
    default_configure = get_default_configure(outername, innername)
    
    if len(default_configure) == 0:
        return (stdin_cases, diff_detail)
    
    # get all the default configuration extracted if the cases going on
    # FIXME: notice that there should also be specific default values in the configuration file
    (all_cases, 
    default_mem_lim, 
    default_cpu_lim, 
    default_clock_lim) = default_configure
    
    exact_cases = [case for case in all_cases if case not in skip_cases]
    
    # given basic templates
    for _, case in enumerate(exact_cases):
        if "e" in innername:
            new_innername = ex2e(innername)
            
        stdin_cases.append({
            "stdin": {
                "src": "/home/tt/.config/joj/" + outername + "/" + new_innername + "/" + case + ".in"
            }
        })
        diff_detail.append({
            "outputs": [
                {
                "score": 100, # TODO: specify how exactly should this score be specified
                "fileName": "stdout",
                "answerPath": "/home/tt/.config/joj/" + outername + "/" + new_innername + "/" + case + ".out"
                }
            ]
        })

    # distribute the basic parametres
    for idx, case in enumerate(exact_cases):
        stdin_cases[idx]['cpuLimit'] = default_cpu_lim
        stdin_cases[idx]['clockLimit'] = default_clock_lim
        stdin_cases[idx]['memoryLimit'] = default_mem_lim
        stdin_cases[idx]['procLimit'] = 50
        
        diff_detail[idx]['outputs'][0]['forceQuitOnDiff'] = True
    
    # specify for special testcases
    for idx, case in enumerate(exact_cases):
        if case in parser_detail:
            continue # TODO: add a function here
        else:
            continue
    
    return (stdin_cases, diff_detail)

def fix_diff(diff_detail, stdin_cases, case, idx, header, loaded_toml):
    '''
    - diff_detail should store with the default cases.out configuration
    - stdin_cases should store withh the default cases.in configuration
    - case should be a single case string name, for example "case4", which help to locate things in the loaded_toml data
    - the index is to help locate things in the diff_detail and stdin_cases, just the index to help filling things
    '''
    case_detail = loaded_toml.get(header, {}).get(case, {})
    for key, value in case_detail.item():
        match "key":
            case "score":
                return 0
            case "limit":
                return 0
            case "output":
                return 0
            case "size":
                return 0
            case _:
                return 0
            
    return 0

# FIXME: in future we may not merely like to migrate the testcases from old yaml configuration
# TODO: add more options, i.e. add an elif, if there is no old yaml configuration, we may have further solution for getting a default cases
def get_default_configure(outername, innername):
    yaml_path = os.path.expanduser("~/.config/joj/" + outername + "/" + innername + "/config.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
            mem_str = yaml_data['default']['memory']
            default_mem_lim = int(mem_str[:-1]) * 1024 * 1024
            time_str = yaml_data['default']['time']
            default_cpu_lim = int(time_str[:-1]) * 1000000000
            default_clock_lim = 2 * default_cpu_lim
            all_cases = yaml_data['cases']
            return (all_cases, default_mem_lim, default_cpu_lim, default_clock_lim)
    else: 
        return ()
