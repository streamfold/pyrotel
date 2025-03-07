# SPDX-License-Identifier: Apache-2.0

import os
from runpy import run_path
from typing import Any


def run_relative(filename: str) -> dict[str, Any]:
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))

PLATFORM_TAGS = run_relative("platform.py")["PLATFORM_TAGS"]

for arch in PLATFORM_TAGS:
    result = os.system(f"_ROTEL_PLATFORM_ARCH={arch} hatch build -t wheel")
    if result != 0:
        break
