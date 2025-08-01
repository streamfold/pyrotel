# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import tempfile

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPGRPCSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    Compression,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPHTTPSpanExporter,
)
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from src.rotel.agent import agent
from src.rotel.client import Client
from src.rotel.config import Config, Options
from tests.utils import wait_until
from tests.utils_server import MockServer


# isort: off
from tests.utils_server import mock_server # noqa: F401
# isort: on


def test_client_connect_http(mock_server):
    addr = mock_server.address()

    client = Client(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = f"http://{addr[0]}:{addr[1]}",
            protocol = "http"
        )
    )
    client.start()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http"

    provider = new_http_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active"):
        pass
    provider.shutdown()

    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    assert MockServer.tracker.get_count() == 1

def test_client_connect_grpc(mock_server):
    addr = mock_server.address()

    client = Client(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = f"http://{addr[0]}:{addr[1]}",
            protocol = "http"
        )
    )
    client.start()

    provider = new_grpc_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active"):
        pass

    provider.shutdown()
    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    assert MockServer.tracker.get_count() == 1

def test_client_custom_headers(mock_server):
    addr = mock_server.address()

    client = Client(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = f"http://{addr[0]}:{addr[1]}",
            protocol = "http",
            headers = {
                "Authorization": "Bearer 12345",
                "X-Dataset": "foobar",
            }
        )
    )
    client.start()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http"

    provider = new_http_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active"):
        pass
    provider.shutdown()

    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    assert MockServer.tracker.get_count() == 1

    req = MockServer.tracker.get_requests()[0]
    assert req.headers.get("Authorization") == "Bearer 12345"
    assert req.headers.get("X-Dataset") == "foobar"

def test_client_datadog(mock_server):
    addr = mock_server.address()

    client = Client(
        enabled = True,
        exporter = Config.datadog_exporter(
            custom_endpoint= f"http://{addr[0]}:{addr[1]}",
            api_key = "987654",
        )
    )
    client.start()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http"

    provider = new_http_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active"):
        pass
    provider.shutdown()

    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    assert MockServer.tracker.get_count() == 1

    req = MockServer.tracker.get_requests()[0]
    assert req.headers.get("DD-API-KEY") == "987654"

def test_client_multiple_exporters(mock_server):
    addr = mock_server.address()

    client = Client(
        enabled = True,
        exporters = {
            'tracing': Config.datadog_exporter(
                custom_endpoint= f"http://{addr[0]}:{addr[1]}",
                api_key = "987a654",
            ),
            'metrics': Config.otlp_exporter(
                endpoint = "http://localhost:4318",
                protocol = "http",
            ),
            'blackhole': Config.blackhole_exporter(),
        },
        exporters_traces = ['tracing'],
        exporters_metrics = ['metrics'],
        exporters_logs = ['blackhole'],
    )
    client.start()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http"

    provider = new_http_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active"):
        pass
    provider.shutdown()

    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    assert MockServer.tracker.get_count() == 1

    req = MockServer.tracker.get_requests()[0]
    assert req.headers.get("DD-API-KEY") == "987a654"

def test_client_clickhouse(mock_server):
    addr = mock_server.address()

    client = Client(
        enabled = True,
        exporter = Config.clickhouse_exporter(
            endpoint = f"http://{addr[0]}:{addr[1]}",
            user = "foobar",
            password = "my-password",
            enable_json = True,
        ),
    )
    client.start()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http"

    provider = new_http_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active"):
        pass
    provider.shutdown()

    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    assert MockServer.tracker.get_count() == 1

    req = MockServer.tracker.get_requests()[0]
    assert req.headers.get("x-clickhouse-user") == "foobar"
    assert req.headers.get("x-clickhouse-key") == "my-password"

def test_client_env_config(mock_server):
    addr = mock_server.address()

    os.environ["ROTEL_ENABLED"] = "true"
    os.environ["ROTEL_OTLP_EXPORTER_ENDPOINT"] = f"http://{addr[0]}:{addr[1]}"
    os.environ["ROTEL_OTLP_EXPORTER_PROTOCOL"] = "http"

    from src.rotel import start
    start()

    provider = new_grpc_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active"):
        pass

    provider.shutdown()
    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    assert MockServer.tracker.get_count() == 1


def test_client_double_start(mock_server):
    addr = mock_server.address()

    opts = Options(
        enabled = True,
        exporter = Config.otlp_exporter(
            endpoint = f"http://{addr[0]}:{addr[1]}",
            protocol = "http"
        )
    )
    cfg = Config(opts)

    res = agent.start(cfg)
    assert res

    # This should ignore the error of binding on an existing port, since we check
    # the pid FILE.
    res2 = agent.start(cfg)
    assert res2

def test_client_processor_traces(mock_server):
    addr = mock_server.address()
    
    tmpfile = tempfile.mktemp()

    client = Client(
        enabled = True,
        log_file=tmpfile,
        debug_log=['traces'],
        debug_log_verbosity = "detailed",
        
        # We use the OTLP exporter so that we can wait for the request
        # to be processed
        exporters = {
            'otlp': Config.otlp_exporter(
                endpoint = f"http://{addr[0]}:{addr[1]}",
                protocol = "http"
            ),
        },
        exporters_traces = ['otlp'],
        processors_traces=[f"{os.path.dirname(os.path.dirname(__file__))}/tests/contrib/trace_processor.py"]
    )
    client.start()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http"

    provider = new_http_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active") as span:
        span.set_attribute("test_attribute", "this_is_a_value")
    provider.shutdown()

    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    assert MockServer.tracker.get_count() == 1
        
    contents = read_file(tmpfile)
    
    assert "test_attribute: Str(this_is_a_value)" in contents
    assert "processed.by: Str(this_is_trace_processor)" in contents
    
    os.remove(tmpfile)

def new_grpc_provider() -> TracerProvider:
    return new_provider(OTLPGRPCSpanExporter(timeout=5, endpoint="http://localhost:4317", insecure=True))

def new_http_provider() -> TracerProvider:
    return new_provider(OTLPHTTPSpanExporter(timeout=5, compression=Compression.Gzip))

def new_provider(exporter) -> TracerProvider:
    resource = Resource(
        attributes={
            SERVICE_NAME: "pyrotel-test",
            DEPLOYMENT_ENVIRONMENT: "test",
        }
    )
    provider = TracerProvider(resource=resource)
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    return provider

def new_tracer(provider: TracerProvider, name: str):
    return provider.get_tracer(name)

def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()