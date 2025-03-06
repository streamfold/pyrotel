from __future__ import annotations

import os
from runpy import run_path

from rotel.client import Client as Rotel
from src.rotel.config import Config, Options, OTLPExporter


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
    assert cfg.options["exporter"]["custom_headers"] == list(["api=1234", "team=8793"])
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
        exporter = OTLPExporter(
            endpoint = "http://foo2.example.com:4317",
            compression = "gzip",
            custom_headers = ["api-key=super-secret", "team=dev"]
        )
    )

    assert cl.config.is_active()
    assert cl.config.options["otlp_grpc_endpoint"] == "localhost:5317"

    exporter = cl.config.options["exporter"]
    assert exporter["endpoint"] == "http://foo2.example.com:4317"
    assert exporter["custom_headers"] == ["api-key=super-secret", "team=dev"]

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_ENDPOINT"] == "localhost:5317"
    assert agent.get("ROTEL_OTLP_EXPORTER") is None
    assert agent["ROTEL_OTLP_EXPORTER_ENDPOINT"] == "http://foo2.example.com:4317"
    assert agent["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] == "api-key=super-secret,team=dev"

def test_config_env_override():
    os.environ["ROTEL_OTLP_GRPC_ENDPOINT"] = "localhost:5317"
    os.environ["ROTEL_OTLP_EXPORTER_ENDPOINT"] = "http://notused.example.com:4318"
    os.environ["ROTEL_OTLP_EXPORTER_PROTOCOL"] = "http"

    cl = Rotel(
        enabled = True,
        exporter = OTLPExporter(
            endpoint = "http://foo2.example.com:4318",
        )
    )

    assert cl.config.is_active()
    assert cl.config.options["otlp_grpc_endpoint"] == "localhost:5317"
    assert cl.config.options["exporter"]["endpoint"] == "http://foo2.example.com:4318"
    assert cl.config.options["exporter"]["protocol"] == "http"

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_ENDPOINT"] == "localhost:5317"
    assert agent["ROTEL_OTLP_EXPORTER_ENDPOINT"] == "http://foo2.example.com:4318"
    assert agent["ROTEL_OTLP_EXPORTER_PROTOCOL"] == "http"

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
        exporter = OTLPExporter(
            endpoint = "http://foo.example.com:4317",
            protocol = "grpc"
        )
    ))
    assert cfg.is_active()

    cfg = Config(Options(
        enabled = True,
        exporter = OTLPExporter(
            endpoint = "http://foo.example.com:4317",
            protocol = "unknown"
        )
    ))
    assert not cfg.is_active()
