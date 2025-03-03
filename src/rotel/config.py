from __future__ import annotations

import os
import re
from typing import Any, ClassVar, List, Literal, TypedDict, cast, get_args

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
        opts.update(self.DEFAULT_OPTIONS)
        opts.update(Config.load_options_from_env())
        if options is not None:
            opts.update(env_sub_opts(options))

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


def replace_env_vars(input_string):
    """
    Replace all occurrences of {UPPERCASE} in a string with corresponding environment variable values.
    """
    def get_env_var(match):
        var_name = match.group(1)  # Extract name without braces
        return os.environ.get(var_name, f"{{{var_name}}}")  # Return original if not found

    # Pattern matches uppercase or underscore letters enclosed in curly braces
    pattern = r'\{([A-Z][A-Z_]*)\}'

    # Replace all matches using the get_env_var function
    return re.sub(pattern, get_env_var, input_string)

def env_sub_value(value: Any) -> Any:
    if isinstance(value, str):
        return replace_env_vars(value)
    return value

def env_sub_list(opts : list[str]) -> list[str]:
    ret = []
    for v in opts:
        ret.append(env_sub_value(v))
    return list(ret)

def env_sub_opts(opts : Options) -> Options:
    for k, v in opts.items():
        if isinstance(v, dict):
            ret = env_sub_opts(v)
            cast(dict, opts)[k] = ret
        elif isinstance(v, list):
            ret = env_sub_list(v)
            cast(dict, opts)[k] = ret
        else:
            ret = env_sub_value(v)
            cast(dict, opts)[k] = ret
    return opts
