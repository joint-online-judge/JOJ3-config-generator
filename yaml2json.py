import yaml
import json
import os


def matlab_json_init():
    output_json = {
        "sandboxExecServer": "172.17.0.1:5051",
        "outputPath": "/tmp/joj3_result.json",
        "stages": []
    }
    healthcheck_json = {
      "name": "healthcheck",
      "executor": {
        "name": "sandbox",
        "with": {
          "default": {
            "args": [
              "./healthcheck",
              "-root=.",
              "-meta=readme",
              "-whitelist=stderr",
              "-whitelist=stdout",
              "-whitelist=.*\\.toml",
              "-whitelist=.*\\.md",
              "-whitelist=healthcheck",
              "-whitelist=.*\\.json",
              "-whitelist=.git.*"
            ],
            "env": [
              "PATH=/usr/bin:/bin"
            ],
            "cpuLimit": 10000000000,
            "memoryLimit": 104857600,
            "procLimit": 50,
            "copyInDir": ".",
            "copyIn": {
              "healthcheck": {
                "src": "./../../../../../../build/healthcheck",
                "copyOut": [
                  "stdout",
                  "stderr"
                ]
              }
            },
            "stdin": {
              "content": ""
            },
            "stdout": {
              "name": "stdout",
              "max": 4096
            },
            "stderr": {
              "name": "stderr",
              "max": 4096
            }
          }
        }
      },
      "parser": {
        "name": "healthcheck",
        "with": {
          "score": 10,
          "comment": " + comment from json conf"
        }
      }
    }
    run_json = {
                "name": "run",
                "executor": {
                    "name": "sandbox",
                    "with": {
                        "default": {
                            "args": [
                                ""
                            ],
                            "env": [
                                "PATH=/usr/bin:/bin"
                            ],
                            "cpuLimit": 20000000000,
                            "memoryLimit": 104857600,
                            "clockLimit": 40000000000,
                            "procLimit": 50,
                            "copyOut": [
                                "stdout",
                                "stderr"
                            ],
                            "stdout": {
                                "name": "stdout",
                                "max": 4096
                            },
                            "stderr": {
                                "name": "stderr",
                                "max": 4096
                            },
                            # matlab don't need this
                            # "copyInCached": {
                            #     "a": "a"
                            # }
                        },
                        "cases": []
                    }
                },
                "parser": {
                    "name": "diff",
                    "with": {
                        "cases": []
                    }
                }
            }
    output_json["stages"].append(healthcheck_json)
    output_json["stages"].append(run_json)
    return output_json

def get_cases(output_json, yaml_data):
    for case in yaml_data['cases']:
        print(yaml_data['cases'])
        input_entry = {
            "stdin":{
                "src": case["input"]
            }
        }
        output_entry = {
            "outputs": {
                "score": 100,
                "fileName": "stdout",
                "answerPath": case["output"]
            }
        }
        output_json["stages"][1]["executor"]["with"]["cases"].append(input_entry)
        output_json["stages"][1]["parser"]["with"]["cases"].append(output_entry)
    return output_json


# Function to merge YAML content into the JSON structure
def yaml_to_custom_json(yaml_file, json_file):
    # Load YAML data from the input file
    with open(yaml_file, 'r') as f:
        yaml_data = yaml.safe_load(f)

    # Define the base JSON structure as per your example
    output_json = matlab_json_init()

    # memory limit migration
    memory_str = yaml_data['default']['memory']
    memory_limit = int(memory_str[:-1]) * 1024 * 1024
    output_json["stages"][0]["executor"]["with"]["default"]["memoryLimit"] = memory_limit

    # time limit migration
    time_str = yaml_data['default']['time']
    cpu_limit = int(time_str[:-1]) * 1000000000
    clock_limit = 2 * cpu_limit
    output_json['stages'][1]["executor"]["with"]["default"]["cpuLimit"] = cpu_limit
    output_json["stages"][1]["executor"]["with"]["default"]["clockLimit"] = clock_limit

    # test cases migration
    # testcases input migration
    # # testcases output migration
    output_json = get_cases(output_json, yaml_data)
    
    # execution args migration
    args = "octave " + assignment_name + ".m"
    output_json["stages"][1]["executor"]["with"]["default"]["args"] = args.split()

    # Write the output JSON to the specified file
    with open(json_file, 'w') as f:
        json.dump(output_json, f, indent=2)

# i/p of files
yaml_file = './ex4/config.yaml'  
json_file = './output.json'
assignment_name = "ex4"
yaml_to_custom_json(yaml_file, json_file)

print(f"YAML content has been successfully converted to JSON and saved to {json_file}")
