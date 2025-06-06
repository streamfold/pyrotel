# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import sysconfig
from runpy import run_path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def run_relative(filename: str) -> dict[str, Any]:
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))

PLATFORM_TAGS = run_relative("platform.py")["PLATFORM_TAGS"]
PLATFORM_FILE_ARCH = run_relative("platform.py")["PLATFORM_FILE_ARCH"]
PLATFORM_PY_VERSIONS = run_relative("platform.py")["PLATFORM_PY_VERSIONS"]

def current_platform_arch():
    platform = sysconfig.get_platform()
    [osname, *_, arch] = platform.split("-")

    if osname == "macosx":
        osname = "darwin"

    if arch == "universal2":
        arch = "arm64"

    if osname == "linux":
        ldd_run = subprocess.run(["ldd", "--version"], capture_output=True, check=False)
        if b"musl" in ldd_run.stderr:
            osname = "linux-musl"

    return f"{arch}-{osname}"

def download_env(agent_arch, py_version, rotel_version):
    download_env = os.environ.copy()
    updates = {
        "ROTEL_ARCH": agent_arch,
        "ROTEL_PY_VERSION": py_version,
        "ROTEL_RELEASE": rotel_version,
    }

    for key, value in updates.items():
        if value is not None:
            download_env[key] = str(value)

    return download_env

def download_agent(script_path, agent_arch, py_version, out_file):
    if not env_not_blank("GITHUB_API_TOKEN"):
        print("must set GITHUB_API_TOKEN to download artifacts")
        exit(1)

    rotel_version = load_rotel_version()
    if not rotel_version:
        print("unable to load rotel version from pyproject.yaml")
        exit(1)

    env = download_env(agent_arch, py_version, rotel_version)

    p = subprocess.Popen(
        [script_path, out_file],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.wait(timeout=120)
    retcode = p.returncode
    if retcode != 0:
        output, outerror = p.communicate()
        out = output.decode("utf-8")
        outerr = outerror.decode("utf-8")
        print(f"Failed to download agent binary (return code: {retcode}): {out}: {outerr}")
        exit(1)

def rm_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass

def env_not_blank(key) -> bool:
    if key not in os.environ:
        return False
    value = os.environ[key]
    return value != ""

class CustomBuildHook(BuildHookInterface):
    def initialize(self, _version: str, build_data: dict[str, Any]) -> None:
        """
        Invoked before each build
        """

        install_agent_path = os.path.join(self.root, "src", "rotel", "rotel-agent")

        platform_arch = os.environ.get("_ROTEL_PLATFORM_ARCH")
        if not platform_arch:
            platform_arch = current_platform_arch()
            print(f"detected build platform {platform_arch}")

        if platform_arch not in PLATFORM_TAGS:
            print(f"unsupported platform_arch: {platform_arch}")
            exit(1)

        py_version = os.environ.get("_ROTEL_PLATFORM_PY_VERSION")
        if not py_version:
            vinfo = sys.version_info
            py_version = f"{vinfo[0]}.{vinfo[1]}"
        if py_version not in PLATFORM_PY_VERSIONS:
            print(f"unsupported python version: {py_version}")
            exit(1)

        py_version_no_dot = py_version.replace(".", "")
        platform_tag = PLATFORM_TAGS[platform_arch]
        build_data["tag"] = f"cp{py_version_no_dot}-cp{py_version_no_dot}-{platform_tag}"
        build_data["pure_python"] = False

        if env_not_blank("_ROTEL_AGENT_PATH"):
            agent_path = os.environ["_ROTEL_AGENT_PATH"]

            if not os.path.isfile(agent_path):
                print(f"agent path at {agent_path} is not a file, exiting")
                exit(1)

            shutil.copy(agent_path, install_agent_path)
            os.chmod(install_agent_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
        else:
            download_script_path = os.path.join(self.root, "scripts", "download-agent.sh")

            tmp_dir = os.path.join(self.root, "tmp", "download", platform_arch, py_version)
            tmp_path = os.path.join(tmp_dir, "rotel.tar.gz")
            os.makedirs(tmp_dir, exist_ok=True)

            rm_file(tmp_path)

            download_arch = PLATFORM_FILE_ARCH[platform_arch]
            download_agent(download_script_path, download_arch, py_version, tmp_path)

            shutil.copy(tmp_path, install_agent_path)
            os.chmod(install_agent_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

            rm_file(tmp_path)

def load_rotel_version() -> str | None:
    cfg = load_pyproject()
    if cfg:
        return cfg.get("tool", {}).get("rotel", {}).get("version")

    return None

def load_pyproject() -> dict[str,Any] | None:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib

    pyproject_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../pyproject.toml")
    try:
        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"Error: pyproject.toml not found at {pyproject_path}")
        return None
    except Exception as e:
        print(f"Error decoding pyproject.toml: {e}")
        return None

