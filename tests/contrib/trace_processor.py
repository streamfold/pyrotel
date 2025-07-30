from rotel_sdk.open_telemetry.common.v1 import AnyValue, KeyValue
from rotel_sdk.open_telemetry.trace.v1 import ResourceSpans


def process_spans(resource_spans: ResourceSpans):
    for scope_spans in resource_spans.scope_spans:
        for span in scope_spans.spans:
            # Add custom attribute to all spans
            span.attributes.append(KeyValue("processed.by", AnyValue("this_is_trace_processor")))