from pathlib import PurePosixPath

from joj3_config_generator.models.common import Memory, Time

DEFAULT_CPU_LIMIT = Time("1s")
DEFAULT_MEMORY_LIMIT = Memory("256m")
DEFAULT_FILE_LIMIT = Memory("32m")
DEFAULT_CASE_SCORE = 5
DEFAULT_CLOCK_LIMIT_MULTIPLIER = 2
DEFAULT_PROC_LIMIT = 50
DEFAULT_PATH_ENV = "PATH=/usr/bin:/bin:/usr/local/bin"

JOJ3_CONFIG_ROOT = PurePosixPath("/home/tt/.config/joj")
TEAPOT_CONFIG_ROOT = PurePosixPath("/home/tt/.config/teapot")
CACHE_ROOT = PurePosixPath("/home/tt/.cache")
JOJ3_LOG_BASE_PATH = CACHE_ROOT / "joj3"
JOJ3_LOG_FILENAME = "joj3.log"
TEAPOT_LOG_PATH = CACHE_ROOT / "joint-teapot-debug.log"
ACTOR_CSV_PATH = JOJ3_CONFIG_ROOT / "students.csv"
