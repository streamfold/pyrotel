from __future__ import annotations

import os
from typing import Any, ClassVar, List, Literal, TypedDict, cast, get_args

class Options(TypedDict, total=False):
    otlp_grpc_port: str | int | None
    otlp_http_port: str | int | None
    pid_file: str | None
    log_file: str | None


class Config:
    DEFAULT_OPTIONS = Options(
        otlp_grpc_port=4317,
        otlp_http_port=4318,
        pid_file="/tmp/rotel-agent.pid",
        log_file="/tmp/rotel-agent.log",
    )

    def __init__(self, options: Options | None = None):
        opts = self.DEFAULT_OPTIONS
        opts.update(Config.load_options_from_env())
        if options is not None:
            opts.update(options)

        self.options = opts

    @staticmethod
    def load_options_from_env() -> Options:
        env = Options(
            otlp_grpc_port=os.environ.get("ROTEL_OTLP_GRPC_PORT"),
            otlp_http_port=os.environ.get("ROTEL_OTLP_HTTP_PORT"),
            pid_file=os.environ.get("ROTAL_PID_FILE"),
            log_file=os.environ.get("ROTEL_LOG_FILE"),
        )
        final_env = Options()

        for key, value in env.items():
            if value is not None:
                cast(dict, final_env)[key] = value
        return final_env

    def build_agent_environment(self) -> dict[str,str]:
        opts = self.options

        spawn_env = os.environ.copy()
        updates = {
            "ROTEL_OTLP_GRPC_PORT": opts.get("otlp_grpc_port"),
            "ROTEL_OTLP_HTTP_PORT": opts.get("otlp_http_port"),
            "ROTEL_PID_FILE": opts.get("pid_file"),
            "ROTEL_LOG_FILE": opts.get("log_file"),
        }
        for key, value in updates.items():
            if value is not None:
                spawn_env[key] = str(value)

        return spawn_env
