from __future__ import annotations

import os
from runpy import run_path

import pytest

from rotel.client import Client as Rotel
from src.rotel.config import Config, Options, OTLPExporter

def test_defaults():
    cfg = Config()

    assert cfg.is_active() == False
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

    assert cfg.is_active() == True
    assert cfg.options["otlp_grpc_endpoint"] == "localhost:5317"
    assert cfg.options["exporter"]["endpoint"] == "http://foo.example.com:4317"
    assert cfg.options["exporter"]["custom_headers"] == list(["api=1234", "team=8793"])
    assert cfg.options["exporter"]["tls_skip_verify"] == True

    agent = cfg.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_ENDPOINT"] == "localhost:5317"
    assert agent.get("ROTEL_OTLP_EXPORTER") is None
    assert agent["ROTEL_OTLP_EXPORTER_ENDPOINT"] == "http://foo.example.com:4317"
    assert agent["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] == "api=1234,team=8793"
    assert agent["ROTEL_OTLP_EXPORTER_TLS_SKIP_VERIFY"] == "True"

def test_config_from_file():
    cfg1_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "rotel_cfg1.py")

    os.environ["OTLP_API"] = "foo2.example.com"
    os.environ["API_KEY"] = "super-secret"
    os.environ["TEAM_NAME"] = "dev"

    cl = run_path(cfg1_path)["rotel"]
    assert isinstance(cl, Rotel)

    assert cl.config.is_active() == True
    assert cl.config.options["otlp_grpc_endpoint"] == "localhost:5317"

    exporter = cl.config.options["exporter"]
    assert exporter["endpoint"] == "http://foo2.example.com:4317"
    assert exporter["custom_headers"] == ["api-key=super-secret", "team=dev"]

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_ENDPOINT"] == "localhost:5317"
    assert agent.get("ROTEL_OTLP_EXPORTER") is None
    assert agent["ROTEL_OTLP_EXPORTER_ENDPOINT"] == "http://foo2.example.com:4317"
    assert agent["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] == "api-key=super-secret,team=dev"

def test_config_validation():
    cfg = Config(Options(
        otlp_grpc_endpoint = "localhost:4317"
    ))
    assert cfg.is_active() == False

    cfg = Config(Options(
        enabled = True
    ))
    assert cfg.is_active() == True

    cfg = Config(Options(
        enabled = True,
        exporter = OTLPExporter(
            endpoint = "http://foo.example.com:4317",
            protocol = "grpc"
        )
    ))
    assert cfg.is_active() == True

    cfg = Config(Options(
        enabled = True,
        exporter = OTLPExporter(
            endpoint = "http://foo.example.com:4317",
            protocol = "unknown"
        )
    ))
    assert cfg.is_active() == False
