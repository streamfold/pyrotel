# rotel 🌶️ 🍅
Python package for the Rotel lightweight OpenTelemetry collector.

[![PyPI - Version](https://img.shields.io/pypi/v/rotel.svg)](https://pypi.org/project/rotel)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rotel.svg)](https://pypi.org/project/rotel)

## Description

This package provides an embedded OpenTelemetry collector, built on the lightweight [Rotel](https://github.com/streamfold/rotel) collector. When started, it spawns a background daemon that accepts OpenTelemetry metrics, traces, and logs. Designed for minimal overhead, Rotel reduces resource consumption while simplifying telemetry collection and processing in complex Python applications—without requiring additional sidecar containers.

By default, the Rotel agent listens for OpenTelemetry data over **gRPC (port 4317)** and **HTTP (port 4318)** on _localhost_. It efficiently batches telemetry signals and forwards them to a configurable OTLP endpoint. Future updates will introduce support for additional filtering, transformations, and exporters.

| Telemetry Type | Support     |
|----------------|-------------|
| Metrics        | Alpha       |
| Traces         | Alpha       |
| Logs           | Coming soon |

## Getting started

### Rotel configuration

Add the `rotel` Python package to your project's dependencies. There are two approaches to configuring rotel:
1. typed config dicts
2. environment variables

#### Typed dicts

In the startup section of your `main.py` add the following code block. Replace the endpoint with the endpoint of your OpenTelemetry vendor and any required API KEY headers. 

```python
from rotel import OTLPExporter, Rotel

rotel = Rotel(
    enabled = True,
    exporter = OTLPExporter(
        endpoint = "https://foo.example.com",
        custom_headers=[f"x-api-key={settings.API_KEY}", "x-data-set=testing"]
    ),
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
* `ROTEL_ENABLED=true`
* `ROTEL_OTLP_EXPORTER_ENDPOINT=https://foo.example.com`
* `ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS=x-api-key={API_KEY}`

Any typed configuration options will override environment variables of the same name.

---

See the [*Configuration*](#configuration) section for the full list of options.

### OpenTelemetry SDK configuration

Once the rotel collector agent is running, you may need to configure your application's instrumentation. If you are using the default rotel endpoints of *localhost:4317* and *localhost:4318*, then you should not need to change anything. 

To set the endpoint the OpenTelemetry SDK will use, set the following environment variable:

* `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`

## Configuration

This is the full list of options and their environment variable alternatives. Any defaults left blank in the table are either False or None.

| Option Name                    | Type         | Environ                              | Default              | Options         |
|--------------------------------|--------------|--------------------------------------|----------------------|-----------------|
| enabled                        | bool         | ROTEL_ENABLED                        |                      |                 |
| pid_file                       | str          | ROTEL_PID_FILE                       | /tmp/rotel-agent.pid |                 |
| log_file                       | str          | ROTEL_LOG_FILE                       | /tmp/rotel-agent.log |                 |
| log_format                     | str          | ROTEL_LOG_FORMAT                     | text                 | json, text      |
| debug_log                      | list[str]    | ROTEL_DEBUG_LOG                      |                      | traces, metrics |
| otlp_grpc_endpoint             | str          | ROTEL_OTLP_GRPC_ENDPOINT             | localhost:4317       |                 |
| otlp_http_endpoint             | str          | ROTEL_OTLP_HTTP_ENDPOINT             | localhost:4318       |                 |
| otlp_receiver_traces_disabled  | bool         | ROTEL_OTLP_RECEIVER_TRACES_DISABLED  |                      |                 |
| otlp_receiver_metrics_disabled | bool         | ROTEL_OTLP_RECEIVER_METRICS_DISABLED |                      |                 |
| exporter                       | OTLPExporter |                                      |                      |                 |

The OTLPExporter can be enabled with the following options.

| Option Name            | Type      | Environ                                    | Default | Options      |
|------------------------|-----------|--------------------------------------------|---------|--------------|
| endpoint               | str       | ROTEL_OTLP_EXPORTER_ENDPOINT               |         |              |
| protocol               | str       | ROTEL_OTLP_EXPORTER_PROTOCOL               | grpc    | grpc or http |
| custom_headers         | list[str] | ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS         |         |              |
| compression            | str       | ROTEL_OTLP_EXPORTER_COMPRESSION            | gzip    | gzip or none |
| request_timeout        | str       | ROTEL_OTLP_EXPORTER_REQUEST_TIMEOUT        | 5s      |              |
| retry_initial_backoff  | str       | ROTEL_OTLP_EXPORTER_RETRY_INITIAL_BACKOFF  | 5s      |              |
| retry_max_backoff      | str       | ROTEL_OTLP_EXPORTER_RETRY_MAX_BACKOFF      | 30s     |              |
| retry_max_elapsed_time | str       | ROTEL_OTLP_EXPORTER_RETRY_MAX_ELAPSED_TIME | 300s    |              |
| batch_max_size         | int       | ROTEL_OTLP_EXPORTER_BATCH_MAX_SIZE         | 8192    |              |
| batch_timeout          | str       | ROTEL_OTLP_EXPORTER_BATCH_TIMEOUT          | 200ms   |              |
| tls_cert_file          | str       | ROTEL_OTLP_EXPORTER_TLS_CERT_FILE          |         |              |
| tls_key_file           | str       | ROTEL_OTLP_EXPORTER_TLS_KEY_FILE           |         |              |
| tls_ca_file            | str       | ROTEL_OTLP_EXPORTER_TLS_CA_FILE            |         |              |
| tls_skip_verify        | bool      | ROTEL_OTLP_EXPORTER_TLS_SKIP_VERIFY        |         |              |

### Endpoint overrides

When using the OTLP exporter over HTTP, the exporter will append `/v1/traces`, `/v1/metrics`, or `/v1/logs` to the endpoint URL for traces, metrics, and logs respectively. If the service you are exporting telemetry data to does not support these standard URL paths, you can individually override them for traces, metrics, and logs.

For example, to override the endpoint for traces and metrics you can do the following:
```python
from rotel import OTLPExporter, OTLPExporterEndpoint, Rotel

rotel = Rotel(
    enabled = True,
    exporter = OTLPExporter(
        custom_headers=[f"x-api-key={settings.API_KEY}"],
        traces = OTLPExporterEndpoint(
            endpoint = "http://foo.example.com:4318/api/otlp/traces",
        ),
        metrics = OTLPExporterEndpoint(
            endpoint = "http://foo.example.com:4318/api/otlp/metrics",
        ),

    ),
)
rotel.start()
```

Or, you can override the endpoints using environment variables:
* `ROTEL_OTLP_EXPORTER_TRACES_ENDPOINT=http://foo.example.com:4318/api/otlp/traces`
* `ROTEL_OTLP_EXPORTER_METRICS_ENDPOINT=http://foo.example.com:4318/api/otlp/metrics`

All the OTLP exporter settings can be overridden per endpoint type (traces, metrics, logs). Any value that is not overridden will fall back to the top-level exporter configuration or the default.

### Retries and timeouts

You can override the default request timeout of 5 seconds for the OTLP Exporter with the exporter setting:

* `request_timeout`: Takes a string time duration, so `"250ms"` for 250 milliseconds, `"3s"` for 3 seconds, etc.

Requests will be retried if they match retryable error codes like 429 (Too Many Requests) or timeout. You can control the behavior with the following exporter options:

* `retry_initial_backoff`: Initial backoff duration
* `retry_max_backoff`: Maximum backoff interval
* `retry_max_elapsed_time`: Maximum wall time a request will be retried for until it is marked as permanent failure

All options should be represented as string time durations.

## Debugging

If you set the option `debug_log` to `["traces"]`, or the environment variable `ROTEL_DEBUG_LOG=traces`, then rotel will log a summary to the log file `/tmp/rotel-agent.log` each time it processes trace spans. You can add also specify *metrics* to debug metrics.   

## Community

Want to chat about this project, share feedback, or suggest improvements? Join our [Discord server](https://discord.gg/reUqNWTSGC)! Whether you're a user of this project or not, we'd love to hear your thoughts and ideas. See you there! 🚀

## Development

Install the latest version of the [hatch](https://hatch.pypa.io/latest/install/) build tool. We'll use this to manage the environments, run tests and perform builds.

### Managing Python versions

Hatch will default to the system's Python version.
If you want to install additional Python versions, you can use `hatch` to manage those.
The following will install Python 3.9:

```shell
hatch python install 3.9
```

Then you can run tests against version 3.9 with:
```shell
hatch run test.py39:pytest
```

### Wheel builds

To build locally using an existing Rotel agent binary, run:
```shell
hatch run build:me ../path/to/agent/file
```

You can always download the latest rotel agent binary from Github. Make sure to create a Github Personal Access Token (PAT) that allows you to pull Github release artifacts. Set that as `GITHUB_API_TOKEN` for the commands below. 

To build using the latest Github built binary:
```shell
GITHUB_API_TOKEN=1234 hatch run build:me
```

Finally, to build for all supported platforms:
```shell
GITHUB_API_TOKEN=1234 hatch run build:all
```

### Linting and formatting

```shell
hatch run lint:fmt    # will fix anything it can, report others
hatch run lint:check  # will only report issues
```

