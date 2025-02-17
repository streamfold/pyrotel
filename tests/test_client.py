import os

import pytest
import rotel

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPGRPCSpanExporter, Compression
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHTTPSpanExporter, Compression
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from tests.utils import wait_until
from tests.utils_server import new_server, MockServer

def test_client_connect_http():
    srv = new_server()
    addr = srv.address()

    # TODO: these will be set with exporter configuration
    os.environ["ROTEL_OTLP_EXPORTER_ENDPOINT"] = f"http://{addr[0]}:{addr[1]}"
    os.environ["ROTEL_OTLP_EXPORTER_PROTOCOL"] = f"http"

    rotel.start()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
    os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "http"

    provider = new_http_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active") as span:
        pass
    provider.shutdown()

    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)
    srv.stop()

    assert MockServer.tracker.get_count() == 1

def test_client_connect_grpc():
    srv = new_server()
    addr = srv.address()

    # TODO: these will be set with exporter configuration
    os.environ["ROTEL_OTLP_EXPORTER_ENDPOINT"] = f"http://{addr[0]}:{addr[1]}"
    os.environ["ROTEL_OTLP_EXPORTER_PROTOCOL"] = f"http"

    rotel.start()

    provider = new_grpc_provider()
    tracer = new_tracer(provider, "pyrotel.test")

    with tracer.start_as_current_span("test_client_active") as span:
        pass

    provider.shutdown()
    wait_until(2, 0.1, lambda: MockServer.tracker.get_count() > 0)

    srv.stop()

    assert MockServer.tracker.get_count() == 1

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
