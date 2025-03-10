# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .config import Config


@dataclass
class Agent:
    pkg_path: Path = Path(__file__).parent
    agent_path: Path = pkg_path / "rotel-agent"
    running: bool = False
    pid_file: str = None

    def start(self, config: Config) -> bool:
        agent_env = config.build_agent_environment()

        p = subprocess.Popen(
            [self.agent_path, "start", "--daemon"],
            env=agent_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            outs, errs = p.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            p.kill()
            outs, errs = p.communicate()
        ret_code = p.returncode
        if ret_code != 0:
            out = outs.decode("utf-8").strip()
            err = errs.decode("utf-8").strip()
            out = " - ".join(filter(None, [out, err]))
            print(f"Rotel agent is unable to start (return code: {ret_code}): {out}")
            return False
        else:
            self.running = True
            self.pid_file = config.options.get("pid_file")
            return True

    def stop(self):
        if self.running is False:
            print("Rotel agent is not running")
            return

        # Could this be bad if the agent died and the PID was recycled?
        # (alternatively could send a shutdown command over an RPC channel)
        if self.pid_file is not None:
            try:
                with open(self.pid_file) as file:
                    line = file.readline()
                    pid = int(line)
                    os.kill(pid, signal.SIGTERM)
                    # wait up to 2.25 secs for this exit
                    time.sleep(0.25)
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
                print("Unable to locate agent pid file")

agent = Agent()
