from pathlib import Path

from joj3_config_generator.models.common import Memory, Time

DEFAULT_CPU_LIMIT = Time("1s")
DEFAULT_MEMORY_LIMIT = Memory("256m")
DEFAULT_FILE_LIMIT = Memory("32m")
DEFAULT_CASE_SCORE = 5

JOJ3_CONFIG_ROOT = Path("/home/tt/.config/joj")
TEAPOT_CONFIG_ROOT = Path("/home/tt/.config/teapot")
CACHE_ROOT = Path("/home/tt/.cache")
JOJ3_LOG_PATH = CACHE_ROOT / "joj3.log"
TEAPOT_LOG_PATH = CACHE_ROOT / "joint-teapot-debug.log"
ACTOR_CSV_PATH = JOJ3_CONFIG_ROOT / "students.csv"
