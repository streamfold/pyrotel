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

class ClickhouseExporter(TypedDict, total=False):
    _type: str | None # set with builder method
    endpoint: str | None
    database: str | None
    table_prefix: str | None
    compression: str | None
    async_insert: bool | None
    user: str | None
    password: str | None

class BlackholeExporter(TypedDict, total=False):
    _type: str | None # set with builder method

class Options(TypedDict, total=False):
    enabled: bool | None
    pid_file: str | None
    log_file: str | None
    log_format: str | None
    debug_log: list[str] | None
    batch_max_size: int | None
    batch_timeout: str | None
    otlp_grpc_endpoint: str | None
    otlp_http_endpoint: str | None
    otlp_receiver_traces_disabled: bool | None
    otlp_receiver_metrics_disabled: bool | None
    otlp_receiver_logs_disabled: bool | None
    exporter: OTLPExporter | DatadogExporter | ClickhouseExporter | BlackholeExporter | None
    # Multiple exporter support
    exporters: dict[str, OTLPExporter | DatadogExporter | ClickhouseExporter | BlackholeExporter] | None
    exporters_metrics: list[str] | None
    exporters_traces: list[str] | None
    exporters_logs: list[str] | None

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
    def clickhouse_exporter(**options: Unpack[ClickhouseExporter]) -> ClickhouseExporter:
        """Construct a Clickhouse exporter config"""
        options["_type"] = "clickhouse"
        return options

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
    def blackhole_exporter() -> BlackholeExporter:
        """Construct a Blackhole exporter config"""
        options = BlackholeExporter()
        options["_type"] = "blackhole"
        return options

    @staticmethod
    def _load_options_from_env() -> Options:
        env = Options(
            enabled = as_bool(rotel_env("ENABLED")),
            pid_file = rotel_env("PID_FILE"),
            log_file = rotel_env("LOG_FILE"),
            log_format = rotel_env("LOG_FORMAT"),
            debug_log = as_list(rotel_env("DEBUG_LOG")),
            batch_max_size = as_int(rotel_env("BATCH_MAX_SIZE")),
            batch_timeout = rotel_env("BATCH_TIMEOUT"),
            otlp_grpc_endpoint = rotel_env("OTLP_GRPC_ENDPOINT"),
            otlp_http_endpoint = rotel_env("OTLP_HTTP_ENDPOINT"),
            otlp_receiver_traces_disabled = as_bool(rotel_env("OTLP_RECEIVER_TRACES_DISABLED")),
            otlp_receiver_metrics_disabled = as_bool(rotel_env("OTLP_RECEIVER_METRICS_DISABLED")),
            otlp_receiver_logs_disabled = as_bool(rotel_env("OTLP_RECEIVER_LOGS_DISABLED")),
        )
        exporters = as_lower(rotel_env("EXPORTERS"))
        if exporters is not None:
            env["exporters"] = {}
            for exporter_str in exporters.split(","):
                name, value = [exporter_str, exporter_str]
                if ":" in exporter_str:
                    name, value = exporter_str.split(":", 1)

                exporter = None
                pfx = f"EXPORTER_{name.upper()}_"
                match value:
                    case "otlp":
                        exporter = Config._load_otlp_exporter_options_from_env(pfx, OTLPExporter)
                        if exporter is None:
                            exporter = OTLPExporter(_type="otlp")

                    case "datadog":
                        exporter = DatadogExporter(
                            _type = "datadog",
                            region = rotel_env(pfx + "REGION"),
                            custom_endpoint = rotel_env(pfx + "CUSTOM_ENDPOINT"),
                            api_key = rotel_env(pfx + "API_KEY"),
                        )

                    case "clickhouse":
                        exporter = ClickhouseExporter(
                            _type = "clickhouse",
                            endpoint = rotel_env(pfx + "ENDPOINT"),
                            database = rotel_env(pfx + "DATABASE"),
                            table_prefix = rotel_env(pfx + "TABLE_PREFIX"),
                            compression = rotel_env(pfx + "COMPRESSION"),
                            async_insert = as_bool(rotel_env(pfx + "ASYNC_INSERT")),
                            user = rotel_env(pfx + "USER"),
                            password = rotel_env(pfx + "PASSWORD"),
                        )
                    case "blackhole":
                        exporter = BlackholeExporter(
                            _type = "blackhole",
                        )

                if exporter is not None:
                    env["exporters"][name] = exporter
            
            env["exporters_traces"] = as_list(rotel_env("EXPORTERS_TRACES"))
            env["exporters_metrics"] = as_list(rotel_env("EXPORTERS_METRICS"))
            env["exporters_logs"] = as_list(rotel_env("EXPORTERS_LOGS"))

        else:
            value = as_lower(rotel_env("EXPORTER"))
            if value is None or value == "otlp":
                exporter = Config._load_otlp_exporter_options_from_env("OTLP_EXPORTER_", OTLPExporter)
                if exporter is None:
                    # make sure we always construct the top-level exporter config
                    exporter = OTLPExporter()
                env["exporter"] = exporter

                endpoint = Config._load_otlp_exporter_options_from_env("OTLP_EXPORTER_TRACES_", OTLPExporterEndpoint)
                if endpoint is not None:
                    exporter["traces"] = endpoint
                endpoint = Config._load_otlp_exporter_options_from_env("OTLP_EXPORTER_METRICS_", OTLPExporterEndpoint)
                if endpoint is not None:
                    exporter["metrics"] = endpoint
                endpoint = Config._load_otlp_exporter_options_from_env("OTLP_EXPORTER_LOGS_", OTLPExporterEndpoint)
                if endpoint is not None:
                    exporter["logs"] = endpoint
            if value == "datadog":
                pfx = "DATADOG_EXPORTER_"
                exporter = DatadogExporter(
                    _type = "datadog",
                    region = rotel_env(pfx + "REGION"),
                    custom_endpoint = rotel_env(pfx + "CUSTOM_ENDPOINT"),
                    api_key = rotel_env(pfx + "API_KEY"),
                )
                env["exporter"] = exporter
            if value == "clickhouse":
                pfx = "CLICKHOUSE_EXPORTER_"
                exporter = ClickhouseExporter(
                    _type = "clickhouse",
                    endpoint = rotel_env(pfx + "ENDPOINT"),
                    database = rotel_env(pfx + "DATABASE"),
                    table_prefix = rotel_env(pfx + "TABLE_PREFIX"),
                    compression = rotel_env(pfx + "COMPRESSION"),
                    async_insert = as_bool(rotel_env(pfx + "ASYNC_INSERT")),
                    user = rotel_env(pfx + "USER"),
                    password = rotel_env(pfx + "PASSWORD"),
                )
                env["exporter"] = exporter

        final_env = Options()

        for name, value in env.items():
            if value is not None:
                cast(dict, final_env)[name] = value
        return final_env

    @staticmethod
    def _load_otlp_exporter_options_from_env(pfx: str, endpoint_class) -> OTLPExporter | OTLPExporterEndpoint | None:
        endpoint = endpoint_class(
            endpoint = rotel_env(pfx + "ENDPOINT"),
            protocol = as_lower(rotel_env(pfx + "PROTOCOL")),
            headers = as_dict(rotel_env(pfx + "CUSTOM_HEADERS")),
            compression = as_lower(rotel_env(pfx + "COMPRESSION")),
            request_timeout = rotel_env(pfx + "REQUEST_TIMEOUT"),
            retry_initial_backoff = rotel_env(pfx + "RETRY_INITIAL_BACKOFF"),
            retry_max_backoff = rotel_env(pfx + "RETRY_MAX_BACKOFF"),
            retry_max_elapsed_time = rotel_env(pfx + "RETRY_MAX_ELAPSED_TIME"),
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
            "BATCH_MAX_SIZE": opts.get("batch_max_size"),
            "BATCH_TIMEOUT": opts.get("batch_timeout"),
            "OTLP_GRPC_ENDPOINT": opts.get("otlp_grpc_endpoint"),
            "OTLP_HTTP_ENDPOINT": opts.get("otlp_http_endpoint"),
            "OTLP_RECEIVER_TRACES_DISABLED": opts.get("otlp_receiver_traces_disabled"),
            "OTLP_RECEIVER_METRICS_DISABLED": opts.get("otlp_receiver_metrics_disabled"),
            "OTLP_RECEIVER_LOGS_DISABLED": opts.get("otlp_receiver_logs_disabled"),
        }

        exporters = opts.get("exporters")
        if exporters:
            exporters_list = []
            for name, exporter in exporters.items():
                exporter_type = cast(dict, exporter).get("_type")
                if name == exporter_type:
                    exporters_list.append(f"{name}")
                else:
                    exporters_list.append(f"{name}:{exporter_type}")

                pfx = f"EXPORTER_{name.upper()}_"
                _set_exporter_agent_env(updates, pfx, exporter)

            updates.update({
                "EXPORTERS": ",".join(exporters_list),
            })

            if opts.get("exporters_metrics") is not None:
                updates.update({
                    "EXPORTERS_METRICS": ",".join(opts.get("exporters_metrics")),
                })
            if opts.get("exporters_traces") is not None:
                updates.update({
                    "EXPORTERS_TRACES": ",".join(opts.get("exporters_traces")),
                })
            if opts.get("exporters_logs") is not None:
                updates.update({
                    "EXPORTERS_LOGS": ",".join(opts.get("exporters_logs")),
                })

        else:
            exporter = opts.get("exporter")
            if exporter:
                _set_exporter_agent_env(updates, None, exporter)

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
            
        exporters = self.options.get("exporters")
        if exporters:
            # Require at least one of exporters_traces, exporters_metrics, exporters_logs
            if all(not self.options.get(x) for x in ["exporters_traces", "exporters_metrics", "exporters_logs"]):
                _errlog("At least one of exporters_traces, exporters_metrics, exporters_logs must be set")
                return False

            # Verify all exporters exist
            for exporters_list_name in ["exporters_traces", "exporters_metrics", "exporters_logs"]:
                exporters_list = self.options.get(exporters_list_name)
                if exporters_list:
                    for exporter_name in exporters_list:
                        if exporter_name not in exporters:
                            _errlog(f"Exporter '{exporter_name}' in {exporters_list_name} not found in exporters config")
                            return False
            
            exporter = self.options.get("exporter")
            if self.options.get("exporter"):
                _errlog("can not use exporters and exporter config together")
                return False

        exporter = self.options.get("exporter")
        if exporter:
            if exporter.get("_type") == "datadog":
                api_key = exporter.get("api_key")
                if not api_key:
                    _errlog("Datadog exporter api_key must be set")
                    return False
            elif exporter.get("_type") == "clickhouse":
                endpoint = exporter.get("endpoint")
                if not endpoint:
                    _errlog("Clickhouse exporter endpoint must be set")
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

def _set_exporter_agent_env(updates: dict, pfx: str | None, exporter: OTLPExporter | DatadogExporter | ClickhouseExporter | BlackholeExporter) -> None:
    exp_type = cast(dict, exporter).get("_type")
    if exp_type == "datadog":
        _set_datadog_exporter_agent_env(updates, pfx, exporter)
        return
    if exp_type == "clickhouse":
        _set_clickhouse_exporter_agent_env(updates, pfx, exporter)
        return
    if exp_type == "blackhole":
        if pfx is None:
            updates.update({
                "EXPORTER": "blackhole"
            })
        return

    #
    # Fall through to OTLP exporter
    #
    _set_otlp_exporter_agent_env(updates, pfx, None, exporter)

    traces = exporter.get("traces")
    if traces is not None:
        _set_otlp_exporter_agent_env(updates, None, "TRACES", traces)

    metrics = exporter.get("metrics")
    if metrics is not None:
        _set_otlp_exporter_agent_env(updates, None, "METRICS", metrics)

    logs = exporter.get("logs")
    if logs is not None:
        _set_otlp_exporter_agent_env(updates, None, "LOGS", metrics)

def _set_datadog_exporter_agent_env(updates: dict, pfx: str | None, exporter: DatadogExporter) -> None:
    if pfx is None:
        pfx = "DATADOG_EXPORTER_"
        # Single exporter config, must set type
        updates.update({
            "EXPORTER": "datadog", # We must opt in to Datadog
        })

    updates.update({
        pfx + "REGION": exporter.get("region"),
        pfx + "CUSTOM_ENDPOINT": exporter.get("custom_endpoint"),
        pfx + "API_KEY": exporter.get("api_key"),
    })

def _set_clickhouse_exporter_agent_env(updates: dict, pfx: str | None, exporter: ClickhouseExporter) -> None:
    if pfx is None:
        pfx = "CLICKHOUSE_EXPORTER_"
        # Single exporter config, must set type
        updates.update({
            "EXPORTER": "clickhouse", # We must opt in to Clickhouse
        })

    updates.update({
        pfx + "ENDPOINT": exporter.get("endpoint"),
        pfx + "DATABASE": exporter.get("database"),
        pfx + "TABLE_PREFIX": exporter.get("table_prefix"),
        pfx + "COMPRESSION": exporter.get("compression"),
        pfx + "ASYNC_INSERT": exporter.get("async_insert"),
        pfx + "USER": exporter.get("user"),
        pfx + "PASSWORD": exporter.get("password"),
    })

def _set_otlp_exporter_agent_env(updates: dict, pfx: str | None, endpoint_type: str | None, exporter: OTLPExporter | OTLPExporterEndpoint | None) -> None:
    if pfx is None:
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
