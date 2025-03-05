from pathlib import Path

from joj3_config_generator.models.common import Memory, Time

DEFAULT_CPU_LIMIT = Time("1s")
DEFAULT_MEMORY_LIMIT = Memory("128m")
DEFAULT_FILE_LIMIT = Memory("32m")

JOJ3_CONFIG_ROOT = Path("/home/tt/.config/joj")
TEAPOT_CONFIG_ROOT = Path("/home/tt/.config/teapot")
CACHE_ROOT = Path("/home/tt/.cache")
