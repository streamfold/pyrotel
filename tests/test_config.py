from __future__ import annotations

import os
from runpy import run_path

import pytest

from rotel.config import Config
from rotel.client import Client as Rotel

from src.rotel import OTLPExporter


def test_defaults():
    cfg = Config()

    assert cfg.options["otlp_grpc_port"] == 4317
    assert cfg.options["otlp_http_port"] == 4318

    agent = cfg.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_PORT"] == "4317"
    assert agent["ROTEL_OTLP_HTTP_PORT"] == "4318"

    assert agent.get("ROTEL_EXPORTER") is None

def test_config_env_basic():
    os.environ["ROTEL_OTLP_GRPC_PORT"] = "5317"
    os.environ["ROTEL_OTLP_EXPORTER_ENDPOINT"] = "http://foo.example.com:4317"
    os.environ["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] = "api=1234,team=8793"
    os.environ["ROTEL_OTLP_EXPORTER_TLS_SKIP_VERIFY"] = "True"

    cfg = Config()

    assert cfg.options["otlp_grpc_port"] == "5317"
    assert cfg.options["exporter"].get("exporter_type") is None
    assert cfg.options["exporter"]["endpoint"] == "http://foo.example.com:4317"
    assert cfg.options["exporter"]["custom_headers"] == list(["api=1234", "team=8793"])
    assert cfg.options["exporter"]["tls_skip_verify"] == True

    agent = cfg.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_PORT"] == "5317"
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

    assert cl.config.options["otlp_grpc_port"] == 5317

    exporter = cl.config.options["exporter"]
    assert exporter["endpoint"] == "http://foo2.example.com:4317"
    assert exporter["custom_headers"] == ["api-key=super-secret", "team=dev"]

    agent = cl.config.build_agent_environment()
    assert agent["ROTEL_OTLP_GRPC_PORT"] == "5317"
    assert agent.get("ROTEL_OTLP_EXPORTER") is None
    assert agent["ROTEL_OTLP_EXPORTER_ENDPOINT"] == "http://foo2.example.com:4317"
    assert agent["ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS"] == "api-key=super-secret,team=dev"
