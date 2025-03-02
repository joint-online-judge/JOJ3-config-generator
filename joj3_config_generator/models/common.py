from typing import Union

import humanfriendly


class Memory(int):
    def __new__(cls, value: Union[str, int]) -> "Memory":
        if isinstance(value, str):
            parsed = humanfriendly.parse_size(value, binary=True)
            return super().__new__(cls, parsed)
        return super().__new__(cls, value)


class Time(int):
    def __new__(cls, value: Union[str, int]) -> "Time":
        if isinstance(value, str):
            parsed = humanfriendly.parse_timespan(value) * 1_000_000_000  # ns
            return super().__new__(cls, round(parsed))
        return super().__new__(cls, value)
