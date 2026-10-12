import platform

import pip


def get_runtime_versions():
    return {
        "python_version": platform.python_version(),
        "pip_version": pip.__version__,
    }
