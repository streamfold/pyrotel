# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sysconfig
from runpy import run_path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def run_relative(filename: str) -> dict[str, Any]:
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))

PLATFORM_TAGS = run_relative("platform.py")["PLATFORM_TAGS"]
PLATFORM_FILE_ARCH = run_relative("platform.py")["PLATFORM_FILE_ARCH"]

ROTEL_RELEASE="v0.0.1-alpha3"

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

def download_env(agent_arch):
    download_env = os.environ.copy()
    updates = {
        "ROTEL_ARCH": agent_arch,
        "ROTEL_RELEASE": ROTEL_RELEASE,
    }
    for key, value in updates.items():
        if value is not None:
            download_env[key] = str(value)

    return download_env

def download_agent(script_path, agent_arch, out_file):
    if not env_not_blank("GITHUB_API_TOKEN"):
        print("must set GITHUB_API_TOKEN to download artifacts")
        exit(1)

    env = download_env(agent_arch)

    p = subprocess.Popen(
        [script_path, out_file],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.wait(timeout=120)
    retcode = p.returncode
    if retcode != 0:
        output, _ = p.communicate()
        out = output.decode("utf-8")
        print(f"Failed to download agent binary (return code: {retcode}): ", out)
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
        platform_arch = None

        if "_ROTEL_PLATFORM_ARCH" in os.environ:
            platform_arch = os.environ["_ROTEL_PLATFORM_ARCH"]
        else:
            platform_arch = current_platform_arch()
            print(f"detected build platform {platform_arch}")

        if platform_arch not in PLATFORM_TAGS:
            print(f"unsupported platform_arch: {platform_arch}")
            exit(1)

        platform_tag = PLATFORM_TAGS[platform_arch]
        build_data["tag"] = f"py3-none-{platform_tag}"
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

            tmp_dir = os.path.join(self.root, "tmp", "download", platform_arch)
            tmp_path = os.path.join(tmp_dir, "rotel.tar.gz")
            os.makedirs(tmp_dir, exist_ok=True)

            rm_file(tmp_path)

            download_arch = PLATFORM_FILE_ARCH[platform_arch]
            download_agent(download_script_path, download_arch, tmp_path)

            shutil.copy(tmp_path, install_agent_path)
            os.chmod(install_agent_path, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)

            rm_file(tmp_path)

