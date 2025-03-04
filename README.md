# pyrotel
Python package for the Rotel lightweight OpenTelemetry collector.

[![PyPI - Version](https://img.shields.io/pypi/v/rotel.svg)](https://pypi.org/project/rotel)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rotel.svg)](https://pypi.org/project/rotel)

## Description

This package provides an embedded OpenTelemetry collector, built on the lightweight [Rotel](https://github.com/streamfold/rotel) collector. When invoked, it spawns a background daemon that accepts OpenTelemetry metrics, traces, and logs. Designed for minimal overhead, Rotel reduces resource consumption while simplifying telemetry collection and processing in complex Python applications—without requiring additional sidecar containers.

By default, the Rotel agent listens for OpenTelemetry (OTel) data over **gRPC (port 4317)** and **HTTP (port 4318)** on _localhost_. It efficiently batches telemetry signals and forwards them to a configurable OTLP endpoint. Future updates will introduce support for additional filtering, transformations, and endpoints.

## Usage

Add the `rotel` Python package to your project's dependencies.

Create the following `__rotel__.py` file and place it at the top of your project directory.

```python
from rotel import Rotel, OTLPExporter

rotel = Rotel(
    exporter = OTLPExporter(
        endpoint="{ROTEL_ENDPOINT}",
    ),
)
```

In your `main.py`, add the following to load the Rotel agent:
```python
import rotel
rotel.start()
```

In your deployment configuration, add the following environment variables to configure Rotel:
* `ROTEL_ENABLED=true` (Rotel will only be started if this is set, allowing you to disable it in dev environments)
* `ROTEL_ENDPOINT=https://foo.example.com` (match to your provider's API endpoint)

To configure the OpenTelemetry SDK, point the exporter configuration to the localhost Rotel agent. Adjust these depending on whether you are using the grpc or http exporter in your code.
* `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`
* `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`

See the configuration documentation for more configuration options.

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

