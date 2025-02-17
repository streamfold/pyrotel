import rotel

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

def test_client_active():
    rotel.start()

    provider = new_provider()
    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer("pyrotel.test")
    with tracer.start_as_current_span("test_client_active") as span:
        pass

def new_provider():
    resource = Resource(
        attributes={
            SERVICE_NAME: "pyrotel-test",
            DEPLOYMENT_ENVIRONMENT: "test",
        }
    )
    provider = TracerProvider(resource=resource)
    processor = SimpleSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    return provider

