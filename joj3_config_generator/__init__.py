try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+development-untracked"


def get_version() -> str:
    return __version__
