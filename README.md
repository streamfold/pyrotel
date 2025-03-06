# pyrotel
Python package for the Rotel lightweight OpenTelemetry collector.

[![PyPI - Version](https://img.shields.io/pypi/v/rotel.svg)](https://pypi.org/project/rotel)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rotel.svg)](https://pypi.org/project/rotel)

## Description

This package provides an embedded OpenTelemetry collector, built on the lightweight [Rotel](https://github.com/streamfold/rotel) collector. When started, it spawns a background daemon that accepts OpenTelemetry metrics, traces, and logs. Designed for minimal overhead, Rotel reduces resource consumption while simplifying telemetry collection and processing in complex Python applications—without requiring additional sidecar containers.

By default, the Rotel agent listens for OpenTelemetry (OTel) data over **gRPC (port 4317)** and **HTTP (port 4318)** on _localhost_. It efficiently batches telemetry signals and forwards them to a configurable OTLP endpoint. Future updates will introduce support for additional filtering, transformations, and exporters.

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
        custom_headers=[f"x-api-key={settings.API_KEY}"]
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

| Option Name        | Type         | Environ                  | Default              | Options         |
|--------------------|--------------|--------------------------|----------------------|-----------------|
| enabled            | bool         | ROTEL_ENABLED            |                      |                 |
| otlp_grpc_endpoint | str          | ROTEL_OTLP_GRPC_ENDPOINT | localhost:4317       |                 |
| otlp_http_endpoint | str          | ROTEL_OTLP_HTTP_ENDPOINT | localhost:4318       |                 |
| pid_file           | str          | ROTEL_PID_FILE           | /tmp/rotel-agent.pid |                 |
| log_file           | str          | ROTEL_LOG_FILE           | /tmp/rotel-agent.log |                 |
| debug_log          | list[str]    | ROTEL_DEBUG_LOG          |                      | traces, metrics |
| exporter           | OTLPExporter |                          |                      |                 |

The OTLPExporter can be enabled with the following options.

| Option Name     | Type      | Environ                             | Default | Options      |
|-----------------|-----------|-------------------------------------|---------|--------------|
| endpoint        | str       | ROTEL_OTLP_EXPORTER_ENDPOINT        |         |              |
| protocol        | str       | ROTEL_OTLP_EXPORTER_PROTOCOL        | grpc    | grpc or http |
| custom_headers  | list[str] | ROTEL_OTLP_EXPORTER_CUSTOM_HEADERS  |         |              |
| compression     | str       | ROTEL_OTLP_EXPORTER_COMPRESSION     | gzip    | gzip or none |
| tls_cert_file   | str       | ROTEL_OTLP_EXPORTER_TLS_CERT_FILE   |         |              |
| tls_key_file    | str       | ROTEL_OTLP_EXPORTER_TLS_KEY_FILE    |         |              |
| tls_ca_file     | str       | ROTEL_OTLP_EXPORTER_TLS_CA_FILE     |         |              |
| tls_skip_verify | bool      | ROTEL_OTLP_EXPORTER_TLS_SKIP_VERIFY |         |              |

## Debugging

If you set the option `debug_log` to `["traces"]`, or the environment variable `ROTEL_DEBUG_LOG=traces`, then rotel will log a summary to the log file `/tmp/rotel-agent.log` each time it processes trace spans. You can add also specify *metrics* to debug metrics.   

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

