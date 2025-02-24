from __future__ import annotations

try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

from .config import Options, Config
from .agent import agent

_client: Client | None = None

class Client:
    def __init__(self, **options: Unpack[Options]):
        global _client
        self.config = Config(options)

        _client = self

    @classmethod
    def get(cls) -> Client:
        return _client

    def start(self):
        if self.config.is_active():
            agent.start(self.config)

    def stop(self):
        if self.config.is_active():
            agent.stop()
