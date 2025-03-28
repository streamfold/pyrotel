# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from typing import TypedDict, cast


try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

from .error import _errlog


class OTLPExporterEndpoint(TypedDict, total=False):
    endpoint: str | None
    protocol: str | None
    headers: dict[str, str] | None
    compression: str | None
    request_timeout: str | None
    retry_initial_backoff: str | None
    retry_max_backoff: str | None
    retry_max_elapsed_time: str | None
    batch_max_size: int | None
    batch_timeout: str | None
    tls_cert_file: str | None
    tls_key_file: str | None
    tls_ca_file: str | None
    tls_skip_verify: bool | None

# TODO: when we have more, include a key that defines this exporter type
class OTLPExporter(TypedDict, total=False):
    _type: str | None
    endpoint: str | None
    protocol: str | None
    headers: dict[str, str] | None
    compression: str | None
    request_timeout: str | None
    retry_initial_backoff: str | None
    retry_max_backoff: str | None
    retry_max_elapsed_time: str | None
    batch_max_size: int | None
    batch_timeout: str | None
    tls_cert_file: str | None
    tls_key_file: str | None
    tls_ca_file: str | None
    tls_skip_verify: bool | None

    traces: OTLPExporterEndpoint | None
    metrics: OTLPExporterEndpoint | None
    logs: OTLPExporterEndpoint | None

class DatadogExporter(TypedDict, total=False):
    _type: str | None # set with builder method
    region: str | None
    custom_endpoint: str | None
    api_key: str | None

class Options(TypedDict, total=False):
    enabled: bool | None
    pid_file: str | None
    log_file: str | None
    log_format: str | None
    debug_log: list[str] | None
    otlp_grpc_endpoint: str | None
    otlp_http_endpoint: str | None
    otlp_receiver_traces_disabled: bool | None
    otlp_receiver_metrics_disabled: bool | None
    otlp_receiver_logs_disabled: bool | None
    exporter: OTLPExporter | DatadogExporter | None

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
        deep_merge_options(opts, Config._load_options_from_env())
        if options is not None:
            deep_merge_options(opts, options)

        self.options = opts
        self.valid = self.validate()

    def is_active(self) -> bool:
        return self.options["enabled"] and self.valid

    @staticmethod
    def datadog_exporter(**options: Unpack[DatadogExporter]) -> DatadogExporter:
        """Construct a Datadog exporter config"""
        options["_type"] = "datadog"
        return options

    @staticmethod
    def otlp_exporter(**options: Unpack[OTLPExporter]) -> OTLPExporter:
        """Construct an OTLP exporter config"""
        options["_type"] = "otlp"
        return options

    @staticmethod
    def _load_options_from_env() -> Options:
        env = Options(
            enabled = as_bool(rotel_env("ENABLED")),
            pid_file = rotel_env("PID_FILE"),
            log_file = rotel_env("LOG_FILE"),
            log_format = rotel_env("LOG_FORMAT"),
            debug_log = as_list(rotel_env("DEBUG_LOG")),
            otlp_grpc_endpoint = rotel_env("OTLP_GRPC_ENDPOINT"),
            otlp_http_endpoint = rotel_env("OTLP_HTTP_ENDPOINT"),
            otlp_receiver_traces_disabled = as_bool(rotel_env("OTLP_RECEIVER_TRACES_DISABLED")),
            otlp_receiver_metrics_disabled = as_bool(rotel_env("OTLP_RECEIVER_METRICS_DISABLED")),
            otlp_receiver_logs_disabled = as_bool(rotel_env("OTLP_RECEIVER_LOGS_DISABLED")),
        )

        exporter_type = as_lower(rotel_env("EXPORTER"))
        if exporter_type is None or exporter_type == "otlp":
            exporter = Config._load_otlp_exporter_options_from_env(None, OTLPExporter)
            if exporter is None:
                # make sure we always construct the top-level exporter config
                exporter = OTLPExporter()
            env["exporter"] = exporter

            endpoint = Config._load_otlp_exporter_options_from_env("TRACES", OTLPExporterEndpoint)
            if endpoint is not None:
                exporter["traces"] = endpoint
            endpoint = Config._load_otlp_exporter_options_from_env("METRICS", OTLPExporterEndpoint)
            if endpoint is not None:
                exporter["metrics"] = endpoint
            endpoint = Config._load_otlp_exporter_options_from_env("LOGS", OTLPExporterEndpoint)
            if endpoint is not None:
                exporter["logs"] = endpoint
        if exporter_type == "datadog":
            pfx = "DATADOG_EXPORTER_"
            exporter = DatadogExporter(
                _type = "datadog",
                region = rotel_env(pfx + "REGION"),
                custom_endpoint = rotel_env(pfx + "CUSTOM_ENDPOINT"),
                api_key = rotel_env(pfx + "API_KEY"),
            )
            env["exporter"] = exporter

        final_env = Options()

        for key, value in env.items():
            if value is not None:
                cast(dict, final_env)[key] = value
        return final_env

    @staticmethod
    def _load_otlp_exporter_options_from_env(endpoint_type: str | None, endpoint_class) -> OTLPExporter | OTLPExporterEndpoint | None:
        pfx = "OTLP_EXPORTER_"
        if endpoint_type is not None:
            pfx += f"{endpoint_type}_"
        endpoint = endpoint_class(
            endpoint = rotel_env(pfx + "ENDPOINT"),
            protocol = as_lower(rotel_env(pfx + "PROTOCOL")),
            headers = as_dict(rotel_env(pfx + "CUSTOM_HEADERS")),
            compression = as_lower(rotel_env(pfx + "COMPRESSION")),
            request_timeout = rotel_env(pfx + "REQUEST_TIMEOUT"),
            retry_initial_backoff = rotel_env(pfx + "RETRY_INITIAL_BACKOFF"),
            retry_max_backoff = rotel_env(pfx + "RETRY_MAX_BACKOFF"),
            retry_max_elapsed_time = rotel_env(pfx + "RETRY_MAX_ELAPSED_TIME"),
            batch_max_size = as_int(rotel_env(pfx + "BATCH_MAX_SIZE")),
            batch_timeout = rotel_env(pfx + "BATCH_TIMEOUT"),
            tls_cert_file = rotel_env(pfx + "TLS_CERT_FILE"),
            tls_key_file = rotel_env(pfx + "TLS_KEY_FILE"),
            tls_ca_file = rotel_env(pfx + "TLS_CA_FILE"),
            tls_skip_verify = as_bool(rotel_env(pfx + "TLS_SKIP_VERIFY"))
        )
        # if any field is set, return the endpoint config, otherwise None
        for k, v in endpoint.items():
            if v is not None:
                return endpoint
        return None

    def build_agent_environment(self) -> dict[str,str]:
        opts = self.options

        spawn_env = os.environ.copy()
        updates = {
            "PID_FILE": opts.get("pid_file"),
            "LOG_FILE": opts.get("log_file"),
            "LOG_FORMAT": opts.get("log_format"),
            "DEBUG_LOG": opts.get("debug_log"),
            "OTLP_GRPC_ENDPOINT": opts.get("otlp_grpc_endpoint"),
            "OTLP_HTTP_ENDPOINT": opts.get("otlp_http_endpoint"),
            "OTLP_RECEIVER_TRACES_DISABLED": opts.get("otlp_receiver_traces_disabled"),
            "OTLP_RECEIVER_METRICS_DISABLED": opts.get("otlp_receiver_metrics_disabled"),
            "OTLP_RECEIVER_LOGS_DISABLED": opts.get("otlp_receiver_logs_disabled"),
        }
        exporter = opts.get("exporter")
        if exporter is not None:
            _set_exporter_agent_env(updates, exporter)

        for key, value in updates.items():
            if value is not None:
                if isinstance(value, list):
                    value = ",".join(value)
                if isinstance(value, dict):
                    hdr_list = []
                    for k, v in value.items():
                        hdr_list.append(f"{k}={v}")
                    value = ",".join(hdr_list)
                rotel_key = rotel_expand_env_key(key)
                spawn_env[rotel_key] = str(value)

        return spawn_env

    # Perform some minimal validation for now, we can expand this as needed
    def validate(self) -> bool | None:
        if not self.options.get("enabled"):
            return None

        exporter = self.options.get("exporter")
        if exporter is not None:
            if exporter.get("_type") == "datadog":
                api_key = exporter.get("api_key")
                if not api_key:
                    _errlog("Datadog exporter api_key must be set")
                    return False
            else:
                protocol = exporter.get("protocol")
                if protocol is not None and protocol not in {'grpc', 'http'}:
                    _errlog("OTLP exporter protocol must be 'grpc' or 'http'")
                    return False

        log_format = self.options.get("log_format")
        if log_format is not None and log_format not in {'json', 'text'}:
            _errlog("log_format must be 'json' or 'text'")
            return False

        return True

def _set_exporter_agent_env(updates: dict, exporter: OTLPExporter | DatadogExporter) -> None:
    exp_type = cast(dict, exporter).get("_type")
    if exp_type == "datadog":
        _set_datadog_exporter_agent_env(updates, exporter)
        return

    #
    # If not Datadog, assume OTLP exporter
    #
    _set_otlp_exporter_agent_env(updates, None, exporter)

    traces = exporter.get("traces")
    if traces is not None:
        _set_otlp_exporter_agent_env(updates, "TRACES", traces)

    metrics = exporter.get("metrics")
    if metrics is not None:
        _set_otlp_exporter_agent_env(updates, "METRICS", metrics)

    logs = exporter.get("logs")
    if logs is not None:
        _set_otlp_exporter_agent_env(updates, "LOGS", metrics)

def _set_datadog_exporter_agent_env(updates: dict, exporter: DatadogExporter) -> None:
    pfx = "DATADOG_EXPORTER_"

    updates.update({
        "EXPORTER": "datadog", # We must opt in to Datadog
        pfx + "REGION": exporter.get("region"),
        pfx + "CUSTOM_ENDPOINT": exporter.get("custom_endpoint"),
        pfx + "API_KEY": exporter.get("api_key"),
    })

def _set_otlp_exporter_agent_env(updates: dict, endpoint_type: str | None, exporter: OTLPExporter | OTLPExporterEndpoint | None) -> None:
    pfx = "OTLP_EXPORTER_"
    if endpoint_type is not None:
        pfx += f"{endpoint_type}_"
    updates.update({
        pfx + "ENDPOINT": exporter.get("endpoint"),
        pfx + "PROTOCOL": exporter.get("protocol"),
        pfx + "CUSTOM_HEADERS": exporter.get("headers"),
        pfx + "COMPRESSION": exporter.get("compression"),
        pfx + "REQUEST_TIMEOUT": exporter.get("request_timeout"),
        pfx + "RETRY_INITIAL_BACKOFF": exporter.get("retry_initial_backoff"),
        pfx + "RETRY_MAX_BACKOFF": exporter.get("retry_max_backoff"),
        pfx + "RETRY_MAX_ELAPSED_TIME": exporter.get("retry_max_elapsed_time"),
        pfx + "BATCH_MAX_SIZE": exporter.get("batch_max_size"),
        pfx + "BATCH_TIMEOUT": exporter.get("batch_timeout"),
        pfx + "TLS_CERT_FILE": exporter.get("tls_cert_file"),
        pfx + "TLS_KEY_FILE": exporter.get("tls_key_file"),
        pfx + "TLS_CA_FILE": exporter.get("tls_ca_file"),
        pfx + "TLS_SKIP_VERIFY": exporter.get("tls_skip_verify"),
    })

def as_dict(value: str | None) -> dict[str, str] | None:
    if value is None:
        return None

    headers = {}
    for hdr_kv in value.split(","):
        hdr_split = hdr_kv.split("=", 1)
        if len(hdr_split) != 2:
            continue
        headers[hdr_split[0]] = hdr_split[1]

    return headers

def as_lower(value: str | None) -> str | None:
    if value is not None:
        return value.lower()
    return value

def as_list(value: str | None) -> list[str] | None:
    if value is not None:
        return value.split(",")
    return None

def as_int(value: str | None) -> int | None:
    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
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
