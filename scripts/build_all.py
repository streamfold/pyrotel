# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from runpy import run_path
from typing import Any


def run_relative(filename: str) -> dict[str, Any]:
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))

PLATFORM_TAGS = run_relative("platform.py")["PLATFORM_TAGS"]
PLATFORM_PY_VERSIONS = run_relative("platform.py")["PLATFORM_PY_VERSIONS"]

for arch in PLATFORM_TAGS:
    for pyver in PLATFORM_PY_VERSIONS:
        result = os.system(f"_ROTEL_PLATFORM_ARCH={arch} _ROTEL_PLATFORM_PY_VERSION={pyver} hatch build -t wheel")
        if result != 0:
            exit(1)
