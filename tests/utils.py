# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import time


def wait_until(max_wait_secs: int, increment: float, test_fn):
    limit = float(max_wait_secs)
    total = 0.0

    while not test_fn():
        time.sleep(increment)

        total += increment
        assert total < limit
