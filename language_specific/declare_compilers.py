import os
import json

class compiled:
        def __init__(self, name, path, args):
                self.name = name
                self.path = path
                self.args = args

class define_compiled:
        def get_compiled():
                for i in os.listdir(os.path.dirname(__file__) + "/compiled"):
                        pass