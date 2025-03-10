# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations


try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

from .agent import agent
from .config import Config, Options


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
