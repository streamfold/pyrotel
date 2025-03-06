from __future__ import annotations

import os
from typing import TypedDict, cast


# TODO: when we have more, include a key that defines this exporter type
class OTLPExporter(TypedDict, total=False):
    endpoint: str | None
    protocol: str | None
    custom_headers: list[str] | None
    compression: str | None
    tls_cert_file: str | None
    tls_key_file: str | None
    tls_ca_file: str | None
    tls_skip_verify: bool | None

class Options(TypedDict, total=False):
    enabled: bool | None
    otlp_grpc_endpoint: str | None
    otlp_http_endpoint: str | None
    pid_file: str | None
    log_file: str | None
    debug_log: list[str] | None
    exporter: OTLPExporter | None

class Config:
    DEFAULT_OPTIONS = Options(
        enabled = False,
        otlp_grpc_endpoint = "localhost:4317",
        otlp_http_endpoint = "localhost:4318",
        pid_file = "/tmp/rotel-agent.pid",
        log_file = "/tmp/rotel-agent.log",
    )

    def __init__(self, options: Options | None = None):
        opts = Options()
        deep_merge_options(opts, self.DEFAULT_OPTIONS)
        deep_merge_options(opts, Config.load_options_from_env())
        if options is not None:
            deep_merge_options(opts, options)

        self.options = opts
        self.valid = self.validate()

    def is_active(self) -> bool:
        return self.options["enabled"] and self.valid

    @staticmethod
    def load_options_from_env() -> Options:
        env = Options(
            enabled = as_bool(rotel_env("ENABLED")),
            otlp_grpc_endpoint = rotel_env("OTLP_GRPC_ENDPOINT"),
            otlp_http_endpoint = rotel_env("OTLP_HTTP_ENDPOINT"),
            pid_file = rotel_env("PID_FILE"),
            log_file = rotel_env("LOG_FILE"),
            debug_log = as_list(rotel_env("DEBUG_LOG"))
        )

        exporter_type = as_lower(rotel_env("EXPORTER"))
        if exporter_type is None or exporter_type == "otlp":
            pfx = "OTLP_EXPORTER_"
            env["exporter"] = OTLPExporter(
                endpoint = rotel_env(pfx + "ENDPOINT"),
                protocol = as_lower(rotel_env(pfx + "PROTOCOL")),
                custom_headers = as_list(rotel_env(pfx + "CUSTOM_HEADERS")),
                compression = as_lower(rotel_env(pfx + "COMPRESSION")),
                tls_cert_file = rotel_env(pfx + "TLS_CERT_FILE"),
                tls_key_file = rotel_env(pfx + "TLS_KEY_FILE"),
                tls_ca_file = rotel_env(pfx + "TLS_CA_FILE"),
                tls_skip_verify = as_bool(rotel_env(pfx + "TLS_SKIP_VERIFY"))
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
            "OTLP_GRPC_ENDPOINT": opts.get("otlp_grpc_endpoint"),
            "OTLP_HTTP_ENDPOINT": opts.get("otlp_http_endpoint"),
            "PID_FILE": opts.get("pid_file"),
            "LOG_FILE": opts.get("log_file"),
            "DEBUG_LOG": opts.get("debug_log"),
        }
        exporter = opts.get("exporter")
        if exporter is not None:
            pfx = "OTLP_EXPORTER_"
            updates.update({
                pfx + "ENDPOINT": exporter.get("endpoint"),
                pfx + "PROTOCOL": exporter.get("protocol"),
                pfx + "CUSTOM_HEADERS": exporter.get("custom_headers"),
                pfx + "COMPRESSION": exporter.get("compression"),
                pfx + "TLS_CERT_FILE": exporter.get("tls_cert_file"),
                pfx + "TLS_KEY_FILE": exporter.get("tls_key_file"),
                pfx + "TLS_CA_FILE": exporter.get("tls_ca_file"),
                pfx + "TLS_SKIP_VERIFY": exporter.get("tls_skip_verify"),
            })

        for key, value in updates.items():
            if value is not None:
                if isinstance(value, list):
                    value = ",".join(value)
                rotel_key = rotel_expand_env_key(key)
                spawn_env[rotel_key] = str(value)

        return spawn_env

    # Perform some minimal validation for now, we can expand this as needed
    def validate(self) -> bool | None:
        if not self.options["enabled"]:
            return None

        exporter = self.options["exporter"]
        if exporter is not None:
            protocol = exporter.get("protocol")
            if protocol is not None and protocol not in {'grpc', 'http'}:
                return False
        return True


def as_lower(value: str | None) -> str | None:
    if value is not None:
        return value.lower()
    return value

def as_list(value: str | None) -> list[str] | None:
    if value is not None:
        return value.split(",")
    return None

def as_bool(value: str | None) -> bool | None:
    if value is None:
        return None

    value = value.lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return None

def rotel_env(base_key: str) -> str | None:
    return os.environ.get(rotel_expand_env_key(base_key))

def rotel_expand_env_key(key: str) -> str:
    if key.startswith("ROTEL_"):
        return key
    return "ROTEL_" + key.upper()

def deep_merge_options(base: Options, src: Options):
    deep_merge_dicts(cast(dict, base), cast(dict, src))

def deep_merge_dicts(base: dict, src: dict):
    for k, v in src.items():
        if v is None:
            continue
        elif base.get(k) is None:
            base[k] = v
        elif isinstance(v, dict):
            deep_merge_dicts(base[k], v)
        else:
            base[k] = v
