import os
from runpy import run_path

from pre_commit.clientlib import InvalidConfigError

from .client import Client as Rotel
from .config import Config

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

    # TODO: set these conditionally
    os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = "http://localhost:4317"
    os.environ["OTEL_EXPORTER_OTLP_TRACES_PROTOCOL"] = "grpc"
    cl.start()

def stop() -> None:
    cl = Rotel.get()
    if cl is not None:
        cl.stop()
