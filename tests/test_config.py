# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os

from rotel.client import Client as Rotel
from src.rotel.config import Config, Options, OTLPExporterEndpoint


def test_defaults():
    cfg = Config()

    assert not cfg.is_active()
    assert cfg.options["otlp_grpc_endpoint"] == "localhost:4317"
    assert cfg.options["otlp_http_endpoint"] == "localhost:4318"

    agent = cfg.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_ENDPOINT"] == "localhost:4317"
    assert agent["ROTEL_OTLP_HTTP_ENDPOINT"] == "localhost:4318"

    assert agent.get("ROTEL_EXPORTER") is None

def test_config_env_basic():
    os.environ["ROTEL_ENABLED"] = "true"
    os.environ["ROTEL_OTLP_GRPC_ENDPOINT"] = "localhost:5317"
    os.environ["ROTEL_OTLP_EXPORTER_ENDPOINT"] = "http://foo.example.com:4317"
    os.environ["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] = "api=1234,team=8793"
    os.environ["ROTEL_OTLP_EXPORTER_TLS_SKIP_VERIFY"] = "True"

    cfg = Config()

    assert cfg.is_active()
    assert cfg.options["otlp_grpc_endpoint"] == "localhost:5317"
    assert cfg.options["exporter"]["endpoint"] == "http://foo.example.com:4317"
    assert cfg.options["exporter"]["headers"] == {"api": "1234", "team": "8793"}
    assert cfg.options["exporter"]["tls_skip_verify"]

    agent = cfg.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_ENDPOINT"] == "localhost:5317"
    assert agent.get("ROTEL_OTLP_EXPORTER") is None
    assert agent["ROTEL_OTLP_EXPORTER_ENDPOINT"] == "http://foo.example.com:4317"
    assert agent["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] == "api=1234,team=8793"
    assert agent["ROTEL_OTLP_EXPORTER_TLS_SKIP_VERIFY"] == "True"

def test_config_from_options():
    cl = Rotel(
        enabled = True,
        otlp_grpc_endpoint = "localhost:5317",
        exporter = Config.otlp_exporter(
            endpoint = "http://foo2.example.com:4317",
            compression = "gzip",
            headers = {"api-key": "super-secret", "team":"dev"}
        )
    )

    assert cl.config.is_active()
    assert cl.config.options["otlp_grpc_endpoint"] == "localhost:5317"

    exporter = cl.config.options["exporter"]
    assert exporter["endpoint"] == "http://foo2.example.com:4317"

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_ENDPOINT"] == "localhost:5317"
    assert agent.get("ROTEL_OTLP_EXPORTER") is None
    assert agent["ROTEL_OTLP_EXPORTER_ENDPOINT"] == "http://foo2.example.com:4317"
    assert agent["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] == "api-key=super-secret,team=dev"

def test_config_env_override():
    os.environ["ROTEL_OTLP_GRPC_ENDPOINT"] = "localhost:5317"
    os.environ["ROTEL_BATCH_MAX_SIZE"] = "4096"
    os.environ["ROTEL_OTLP_EXPORTER_ENDPOINT"] = "http://notused.example.com:4318"
    os.environ["ROTEL_OTLP_EXPORTER_PROTOCOL"] = "http"
    os.environ["ROTEL_OTLP_EXPORTER_REQUEST_TIMEOUT"] = "1s"

    cl = Rotel(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = "http://foo2.example.com:4318",
        )
    )

    assert cl.config.is_active()
    assert cl.config.options["batch_max_size"] == 4096
    assert cl.config.options["otlp_grpc_endpoint"] == "localhost:5317"
    assert cl.config.options["exporter"]["endpoint"] == "http://foo2.example.com:4318"
    assert cl.config.options["exporter"]["protocol"] == "http"
    assert cl.config.options["exporter"]["request_timeout"] == "1s"

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_BATCH_MAX_SIZE"] == "4096"
    assert agent["ROTEL_OTLP_GRPC_ENDPOINT"] == "localhost:5317"
    assert agent["ROTEL_OTLP_EXPORTER_ENDPOINT"] == "http://foo2.example.com:4318"
    assert agent["ROTEL_OTLP_EXPORTER_PROTOCOL"] == "http"
    assert agent["ROTEL_OTLP_EXPORTER_REQUEST_TIMEOUT"] == "1s"

def test_config_custom_endpoints():
    cl = Rotel(
        enabled = True,
        exporter = Config.otlp_exporter(
            traces = OTLPExporterEndpoint(
                endpoint = "http://foo2.example.com:4318/api/v1/traces",
                compression = "none",
            ),
            metrics = OTLPExporterEndpoint(
                endpoint = "http://foo2.example.com:4318/api/v1/metrics",
            ),
        ),
    )

    assert cl.config.is_active()

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_OTLP_EXPORTER_TRACES_ENDPOINT"] == "http://foo2.example.com:4318/api/v1/traces"
    assert agent["ROTEL_OTLP_EXPORTER_TRACES_COMPRESSION"] == "none"
    assert agent["ROTEL_OTLP_EXPORTER_METRICS_ENDPOINT"] == "http://foo2.example.com:4318/api/v1/metrics"

def test_datadog_exporter():
    cl = Rotel(
        enabled = True,
        exporter = Config.datadog_exporter(
            region = "us3",
            api_key = "2345",
        )
    )

    assert cl.config.is_active()

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_EXPORTER"] == "datadog"
    assert agent["ROTEL_DATADOG_EXPORTER_REGION"] == "us3"
    assert agent["ROTEL_DATADOG_EXPORTER_API_KEY"] == "2345"

    cl = Rotel(
        enabled = True,
        exporter = Config.datadog_exporter(
            region = "us3",
        )
    )
    assert not cl.config.is_active()

def test_clickhouse_exporter():
    cl = Rotel(
        enabled = True,
        exporter = Config.clickhouse_exporter(
            endpoint = "https://aws-ch.example.com",
            user = "default",
            password = "1234",
        )
    )

    assert cl.config.is_active()

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_EXPORTER"] == "clickhouse"
    assert agent["ROTEL_CLICKHOUSE_EXPORTER_USER"] == "default"
    assert agent["ROTEL_CLICKHOUSE_EXPORTER_PASSWORD"] == "1234"

    cl = Rotel(
        enabled = True,
        exporter = Config.clickhouse_exporter(
            user = "default",
            password = "1234",
        )
    )
    assert not cl.config.is_active()

def test_config_invalid_int_no_error():
    os.environ["ROTEL_BATCH_MAX_SIZE"] = "abc" # should not error

    cl = Rotel(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = "http://foo2.example.com:4318",
        ),
    )

    assert cl.config.is_active()
    assert cl.config.options.get("batch_max_size") is None

def test_config_custom_endpoints_from_env():
    os.environ["ROTEL_OTLP_EXPORTER_TRACES_ENDPOINT"] = "http://foo2.example.com:4318/api/v1/traces"
    os.environ["ROTEL_OTLP_EXPORTER_METRICS_ENDPOINT"] = "http://foo2.example.com:4318/api/v1/metrics"

    cl = Rotel(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = "http://foo2.example.com:4318",
        ),
    )

    assert cl.config.is_active()
    assert cl.config.options["exporter"]["traces"]["endpoint"] == "http://foo2.example.com:4318/api/v1/traces"
    assert cl.config.options["exporter"]["metrics"]["endpoint"] == "http://foo2.example.com:4318/api/v1/metrics"

def test_config_custom_headers():
    cl = Rotel(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = "http://foo2.example.com:4318",
            headers = {
                "Authorization": "Bearer 1234",
                "X-Dataset": "foo",
            }
        ),
    )

    assert cl.config.is_active()
    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] == "Authorization=Bearer 1234,X-Dataset=foo"

    # test parsing from environ
    os.environ["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] = "Authorization=Bearer 9876,X-Dataset=blah=foo,X-Team=dev"
    cl = Rotel(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = "http://foo2.example.com:4318",
        ),
    )

    assert cl.config.is_active()
    assert cl.config.options["exporter"]["headers"] == {"Authorization": "Bearer 9876", "X-Dataset": "blah=foo", "X-Team": "dev"}

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] == "Authorization=Bearer 9876,X-Dataset=blah=foo,X-Team=dev"


def test_config_validation():
    cfg = Config(Options(
        otlp_grpc_endpoint = "localhost:4317"
    ))
    assert not cfg.is_active()

    cfg = Config(Options(
        enabled = True
    ))
    assert cfg.is_active()

    cfg = Config(Options(
        enabled = True,
        batch_max_size = 4096,
        exporter = Config.otlp_exporter(
            endpoint = "http://foo.example.com:4317",
            protocol = "grpc",
        )
    ))
    assert cfg.is_active()

    # invalid protocol
    cfg = Config(Options(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = "http://foo.example.com:4317",
            protocol = "unknown"
        )
    ))
    assert not cfg.is_active()

    # invalid log format
    cfg = Config(Options(
        enabled = True,
        log_format = "csv",
        exporter = Config.otlp_exporter(
            endpoint = "http://foo.example.com:4317",
        )
    ))
    assert not cfg.is_active()
