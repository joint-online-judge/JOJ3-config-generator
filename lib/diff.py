import tomllib
import json
import os

# TODO: fix the diff parser format as well as the stdin part
# FIXME: feels fix_diff would have different input
def fix_diff(parser_list, parser, key, value, idx):
    if parser != "diff":
        return parser

    if not parser_list[idx]['with']['cases']:
        for _, _ in enumerate(value):
            parser_list[idx]['with']['cases'].append({
                "outputs": [
                    {
                        
                    }
                ]
            })

def get_default_configure():
    return 0
