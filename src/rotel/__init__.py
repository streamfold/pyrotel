from __future__ import annotations

import os
from runpy import run_path

from .client import Client as Rotel
from .config import Config, OTLPExporter

def _client_with_config() -> Rotel:
    # todo: load additional configuration?
    cwd = os.getcwd()
    cfg_path = os.path.join(cwd, "__rotel__.py")
    if os.path.exists(cfg_path):
        try:
            cl = run_path(cfg_path)["rotel"]
            if not isinstance(cl, Rotel):
                raise InvalidConfigError("The __rotel__.py file is invalid")
            return cl
        except KeyError as error:
            raise InvalidConfigError("The __rotel__.py file is invalid")
    # Use defaults
    return Rotel()

def _must_initialize_client() -> Rotel:
    cl = _client_with_config()
    if cl:
        return cl

    # fall back to defaults and environment config
    return Rotel()

def start() -> None:
    cl = _must_initialize_client()
    cl.start()

def stop() -> None:
    cl = Rotel.get()
    if cl is not None:
        cl.stop()

class InvalidConfigError(Exception):
    pass
