import os


class compiled:
    def __init__(self, name: str, path: str, args: list[str]) -> None:
        self.name = name
        self.path = path
        self.args = args


class define_compiled:
    def get_compiled(self) -> None:
        for i in os.listdir(os.path.dirname(__file__) + "/compiled"):
            pass
