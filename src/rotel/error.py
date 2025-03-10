# SPDX-License-Identifier: Apache-2.0

import logging
from logging import Logger


def _errlog(msg: str) -> None:
    log = _get_logger()
    log.error(f"{msg}")

def _get_logger() -> Logger:
    return logging.getLogger("rotel")
