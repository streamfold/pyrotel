# pyrotel
Python module for the Rotel integrated high performance Open Telemetry collector.

# Usage

Add the `rotel` Python module to your project's dependencies and put the following file in your
project's root directory.

`__rotel__.py`:
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
* `ROTEL_ENABLED=true`
* `ROTEL_ENDPOINT=https://foo.example.com` (match to your provider's API endpoint)

To configure the OpenTelemetry SDK, point the exporter configuration to the localhost Rotel agent. Adjust these depending on whether you are using the grpc or http exporter in your code.
* `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`
* `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`

See the configuration documentation for more configuration options.

# Development

Install the latest version of the [hatch](https://hatch.pypa.io/latest/install/) build tool. We'll use this to manage the environments, run tests and perform builds.

## Managing Python versions

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

## Wheel builds

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
