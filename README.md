# rotel 🌶️ 🍅

Python package for the Rotel lightweight OpenTelemetry collector.

[![PyPI - Version](https://img.shields.io/pypi/v/rotel.svg)](https://pypi.org/project/rotel)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rotel.svg)](https://pypi.org/project/rotel)

## Description

This package provides an embedded OpenTelemetry collector, built on the lightweight [Rotel collector](https://github.com/streamfold/rotel). When started, it spawns a background daemon that accepts OpenTelemetry metrics, traces, and logs. Designed for minimal overhead, Rotel reduces resource consumption while simplifying telemetry collection and processing in complex Python applications—without requiring additional sidecar containers.

| Telemetry Type | Support |
| -------------- | ------- |
| Metrics        | Alpha   |
| Traces         | Alpha   |
| Logs           | Alpha   |

## How it works

By default, the Rotel agent listens for OpenTelemetry data over **gRPC (port 4317)** and **HTTP (port 4318)** on _localhost_. It efficiently batches telemetry signals and forwards them to a configurable OpenTelemetry protocol (OTLP) compatible endpoint.

In your application, you use the [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/) to add instrumentation for traces, metrics, and logs. The SDK by default will communicate over ports 4317 or 4318 on _localhost_ to the Rotel agent. You can now ship your instrumented application and efficiently export OpenTelemetry data to your vendor or observability tool of choice with a single deployment artifact.

Future updates will introduce support for filtering data, transforming telemetry, and exporting to different vendors and tools.

## Getting started

### Rotel configuration

Add the `rotel` Python package to your project's dependencies. There are two approaches to configuring rotel:

1. typed config dicts
2. environment variables

#### Typed dicts

In the startup section of your `main.py` add the following code block. Replace the endpoint with the endpoint of your OpenTelemetry vendor and any required API KEY headers.

```python
from rotel import Config, Rotel

rotel = Rotel(
    enabled = True,
    exporters = {
        'otlp': Config.otlp_exporter(
            endpoint = "https://foo.example.com",
            headers = {
                "x-api-key" : settings.API_KEY,
                "x-data-set": "testing"
            }
        ),
    },
    # Define exporters per telemetry type
    exporters_traces = ['otlp'],
    exporters_metrics = ['otlp'],
    exporters_logs = ['otlp']
)
rotel.start()
```

#### Environment variables

You can also configure rotel entirely with environment variables. In your application startup, insert:

```python
import rotel
rotel.start()
```

In your application deployment configuration, set the following environment variables. These match the typed configuration above:

- `ROTEL_ENABLED=true`
- `ROTEL_EXPORTERS=otlp`
- `ROTEL_EXPORTER_OTLP_ENDPOINT=https://foo.example.com`
- `ROTEL_EXPORTER_OTLP_CUSTOM_HEADERS=x-api-key={API_KEY},x-data-set=testing`
- `ROTEL_EXPORTERS_TRACES=otlp`
- `ROTEL_EXPORTERS_METRICS=otlp`
- `ROTEL_EXPORTERS_LOGS=otlp`

Any typed configuration options will override environment variables of the same name.

---

See the [_Configuration_](#configuration) section for the full list of options.

### OpenTelemetry SDK configuration

Once the rotel collector agent is running, you may need to configure your application's instrumentation. If you are using the default rotel endpoints of _localhost:4317_ and _localhost:4318_, then you should not need to change anything.

To set the endpoint the OpenTelemetry SDK will use, set the following environment variable:

- `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`

## Configuration

This is the full list of global options and their environment variable alternatives. Any defaults left blank in the table are either False or None.

| Option Name        | Type      | Environ                  | Default              | Options               |
| ------------------ | --------- | ------------------------ | -------------------- | --------------------- |
| enabled            | bool      | ROTEL_ENABLED            |                      |                       |
| pid_file           | str       | ROTEL_PID_FILE           | /tmp/rotel-agent.pid |                       |
| log_file           | str       | ROTEL_LOG_FILE           | /tmp/rotel-agent.log |                       |
| log_format         | str       | ROTEL_LOG_FORMAT         | text                 | json, text            |
| debug_log          | list[str] | ROTEL_DEBUG_LOG          |                      | traces, metrics, logs |
| otlp_grpc_endpoint | str       | ROTEL_OTLP_GRPC_ENDPOINT | localhost:4317       |                       |
| otlp_http_endpoint | str       | ROTEL_OTLP_HTTP_ENDPOINT | localhost:4318       |                       |

For each exporter you would like to use, see the configuration options below. Exporters should be
assigned to the `exporters` dict with a custom name.

### OTLP Exporter

To construct an OTLP exporter, use the method `Config.otlp_exporter()` with the following options.

| Option Name            | Type           | Default | Options      |
| ---------------------- | -------------- | ------- | ------------ |
| endpoint               | str            |         |              |
| protocol               | str            | grpc    | grpc or http |
| headers                | dict[str, str] |         |              |
| compression            | str            | gzip    | gzip or none |
| request_timeout        | str            | 5s      |              |
| retry_initial_backoff  | str            | 5s      |              |
| retry_max_backoff      | str            | 30s     |              |
| retry_max_elapsed_time | str            | 300s    |              |
| batch_max_size         | int            | 8192    |              |
| batch_timeout          | str            | 200ms   |              |
| tls_cert_file          | str            |         |              |
| tls_key_file           | str            |         |              |
| tls_ca_file            | str            |         |              |
| tls_skip_verify        | bool           |         |              |

### Datadog Exporter

Rotel provides an experimental [Datadog exporter](https://github.com/streamfold/rotel/blob/main/src/exporters/datadog/README.md)
that supports traces at the moment. To use it instead of the OTLP exporter,
use the method `Config.datadog_exporter()` with the following options.

| Option Name     | Type | Default | Options                |
| --------------- | ---- | ------- | ---------------------- |
| region          | str  | us1     | us1, us3, us5, eu, ap1 |
| custom_endpoint | str  |         |                        |
| api_key         | str  |         |                        |

### Clickhouse Exporter

Rotel provides a Clickhouse exporter with support metrics, logs, and traces. To use the Clickhouse exporter instead of the OTLP exporter,
use the method `Config.clickhouse_exporter()` with the following options.

| Option Name  | Type | Default | Options |
| ------------ | ---- | ------- | ------- |
| endpoint     | str  |         |         |
| database     | str  | otel    |         |
| table_prefix | str  | otel    |         |
| compression  | str  | lz4     |         |
| async_insert | bool | true    |         |
| user         | str  |         |         |
| password     | str  |         |         |

### Kafka Exporter

Rotel provides a Kafka exporter with support for metrics, logs, and traces. To use the Kafka exporter instead of the OTLP exporter,
use the method `Config.kafka_exporter()` with the following options.

| Option Name                                | Type | Default           | Options                                                                      |
| ------------------------------------------ | ---- | ----------------- | ---------------------------------------------------------------------------- |
| brokers                                    | list | localhost:9092    |                                                                              |
| traces_topic                               | str  | otlp_traces       |                                                                              |
| logs_topic                                 | str  | otlp_logs         |                                                                              |
| metrics_topic                              | str  | otlp_metrics      |                                                                              |
| format                                     | str  | protobuf          | json, protobuf                                                               |
| compression                                | str  | none              | gzip, snappy, lz4, zstd, none                                                |
| acks                                       | str  | one               | all, one, none                                                               |
| client_id                                  | str  | rotel             |                                                                              |
| max_message_bytes                          | int  | 1000000           |                                                                              |
| linger_ms                                  | int  | 5                 |                                                                              |
| retries                                    | int  | 2147483647        |                                                                              |
| retry_backoff_ms                           | int  | 100               |                                                                              |
| retry_backoff_max_ms                       | int  | 1000              |                                                                              |
| message_timeout_ms                         | int  | 300000            |                                                                              |
| request_timeout_ms                         | int  | 30000             |                                                                              |
| batch_size                                 | int  | 1000000           |                                                                              |
| partitioner                                | str  | consistent-random | consistent, consistent-randomm, murmur2-random, murmur2, fnv1a, fnv1a-random |
| partitioner_metrics_by_resource_attributes | str  | 1000              |                                                                              |
| partitioner_logs_by_resource_attributes    | str  | 1000              |                                                                              |
| custom_config                              | str  | 1000              |                                                                              |
| sasl_username                              | str  |                   |                                                                              |
| sasl_password                              | str  |                   |                                                                              |
| sasl_mechanism                             | str  |                   |                                                                              |
| security_protocol                          | str  | PLAINTEXT         | PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL                                     |

### Multiple exporters

Pyrotel supports [multiple exporters](https://rotel.dev/docs/configuration/multiple-exporters), allowing you to send data to
different destinations per telemetry type. Just set the `exporters` entry to a dict map of exporter definitions and then
configure the exporters per telemetry type. For example, this will send metrics and logs to an OTLP endpoint while
sending traces to Datadog:

```python
from rotel import Config, Rotel

rotel = Rotel(
    enabled = True,
    exporters = {
        'logs_and_metrics': Config.otlp_exporter(
            endpoint = "https://foo.example.com",
            headers = {
                "x-api-key" : settings.API_KEY,
                "x-data-set": "testing"
            }
        ),
        'tracing': Config.datadog_exporter(
            api_key = "1234abcd",
        ),
    },
    # Define exporters per telemetry type
    exporters_traces = ['tracing'],
    exporters_metrics = ['logs_and_metrics'],
    exporters_logs = ['logs_and_metrics']
)
rotel.start()
```

### Retries and timeouts

You can override the default request timeout of 5 seconds for the OTLP Exporter with the exporter setting:

- `request_timeout`: Takes a string time duration, so `"250ms"` for 250 milliseconds, `"3s"` for 3 seconds, etc.

Requests will be retried if they match retryable error codes like 429 (Too Many Requests) or timeout. You can control the behavior with the following exporter options:

- `retry_initial_backoff`: Initial backoff duration
- `retry_max_backoff`: Maximum backoff interval
- `retry_max_elapsed_time`: Maximum wall time a request will be retried for until it is marked as permanent failure

All options should be represented as string time durations.

### Full OTEL example

To illustrate this further, here's a full example of how to use Rotel to send trace spans to [Axiom](https://axiom.co/)
from an application instrumented with OpenTelemetry.

The code sample depends on the following environment variables:

- `ROTEL_ENABLED=true`: Turn on or off based on the deployment environment
- `AXIOM_DATASET`: Name of an Axiom dataset
- `AXIOM_API_TOKEN`: Set to an API token that has access to the Axiom dataset

```python
import os

from rotel import Config, Rotel

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


# Enable at deploy time with ROTEL_ENABLED=true
if os.environ.get("ROTEL_ENABLED") == "true":
    #
    # Configure Rotel to export to Axiom
    #
    otlp_exporter = Config.otlp_exporter(
        endpoint="https://api.axiom.co",
        protocol="http", # Axiom only supports HTTP
        headers={
            "Authorization": f"Bearer {os.environ['AXIOM_API_TOKEN']}",
            "X-Axiom-Dataset": os.environ["AXIOM_DATASET"],
        },
    )

    rotel = Rotel(
        enabled=True,
        exporters = {
            'axiom': otlp_exporter,
        },
        exporters_traces = ['axiom']
    )

    # Start the agent
    rotel.start()

    #
    # Configure OpenTelemetry SDK to export to the localhost Rotel
    #

    # Define the service name resource for the tracer.
    resource = Resource(
        attributes={
            SERVICE_NAME: "pyrotel-test"
        }
    )

    # Create a TracerProvider with the defined resource for creating tracers.
    provider = TracerProvider(resource=resource)

    # Create the OTel exporter to send to the localhost Rotel agent
    exporter = OTLPSpanExporter(endpoint = "http://localhost:4318/v1/traces")

    # Create a processor with the OTLP exporter to send trace spans.
    #
    # You could also use the BatchSpanProcessor, but since Rotel runs locally
    # and will batch, you can avoid double batching.
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)

    # Set the TracerProvider as the global tracer provider.
    trace.set_tracer_provider(provider)
```

For the complete example, see the [hello world](https://github.com/streamfold/pyrotel-hello-world) application.

## Debugging

If you set the option `debug_log` to `["traces"]`, or the environment variable `ROTEL_DEBUG_LOG=traces`, then rotel will log a summary to the log file `/tmp/rotel-agent.log` each time it processes trace spans. You can add also specify _metrics_ to debug metrics and _logs_ to debug logs.

## FAQ

### Do I need to call `rotel.stop()` when I exit?

In most deployment environments you do not need to call `rotel.stop()` and it is **generally recommended that you don't**. Calling `rotel.stop()` will
terminate the running agent on a host, so any further export calls from OTEL instrumentation will fail. In a multiprocess environment, such as
_gunicorn_, terminating the Rotel agent from one process will terminate it for all other processes. On ephemeral deployment platforms, it is
usually fine to leave the agent running until the compute instance, VM/container/isolate, terminate.

## Community

Want to chat about this project, share feedback, or suggest improvements? Join our [Discord server](https://discord.gg/reUqNWTSGC)! Whether you're a user of this project or not, we'd love to hear your thoughts and ideas. See you there! 🚀

## Developing

See the [DEVELOPING.md](DEVELOPING.md) doc for building and development instructions.
