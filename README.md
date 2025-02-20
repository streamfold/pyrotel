# pyrotel
Python module for the Streamfold Rust OpenTelemetry Collector

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
