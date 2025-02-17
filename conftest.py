import os
import signal
import time
from typing import Any

import pytest

from rotel import Config

PID_FILE = "/tmp/rotel-agent.pid"

@pytest.fixture(scope="function", autouse=True)
def restore_environment() -> Any:
    orig_environ = dict(os.environ)

    yield

    os.environ.clear()
    os.environ.update(orig_environ)


@pytest.fixture(scope="function", autouse=True)
def stop_agent() -> Any:
    yield

    pid_file = get_pid_file()
    try:
        with open(pid_file) as file:
            line = file.readline()
            pid = int(line)
            os.kill(pid, signal.SIGTERM)
            # wait up to 2.5secs for this exit
            time.sleep(0.5)
            for i in range(4):
                try:
                    # is this portable?
                    os.kill(pid, 0)
                except OSError:
                    break
                else:
                    time.sleep(0.5)
    except ProcessLookupError:
        pass # In multi-worker configs, the process may have already terminated
    except FileNotFoundError:
        pass


@pytest.fixture(scope="function", autouse=True)
def cleanup_agent() -> Any:
    yield

    # keep the log file for debugging?
    rm_file(get_pid_file())


def rm_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass

def get_pid_file() -> Any:
    return Config.DEFAULT_OPTIONS['pid_file']
