from __future__ import annotations

from .client import Client as Rotel
from .config import Config, OTLPExporter  # noqa: F401


def start() -> None:
    cl = Rotel()
    cl.start()

def stop() -> None:
    cl = Rotel.get()
    if cl is not None:
        cl.stop()
