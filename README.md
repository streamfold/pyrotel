# pyrotel
Python module for the Streamfold Rust OpenTelemetry Collector

# Development

## Hatch builds

First, make sure to install the [hatch](https://hatch.pypa.io/latest/install/) build tool.

To build locally using an existing Rotel agent binary, run:
```shell
$ hatch run build:me ../path/to/agent/file
```

To build using the latest Github built binary:
```shell
$ GITHUB_API_TOKEN=1234 hatch run build:me
```

Finally, to build for all supported platforms:
```shell
$ GITHUB_API_TOKEN=1234 hatch run build:all
```
