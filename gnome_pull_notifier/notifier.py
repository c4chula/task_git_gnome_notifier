from collections.abc import Mapping
from pathlib import PosixPath, Path
from gnome_pull_notifier.daemon import Daemon
import time
import sys
import signal
import os

import gi # type: ignore
gi.require_version('Notify', '0.7')

from gi.repository import Notify
from typing import Any, Dict

from typing import Sequence

import subprocess

PIDFILE_LOCATION = "/tmp/git-notifier.pid"

class GitNotifier(Daemon):

    def __init__(self, *args: Sequence[Any], **kwargs: Dict[str, Any]) -> None:
        self.repo_paths: Mapping[str,PosixPath] = {} 
        super().__init__(*args, **kwargs)

    def add_repo(self, repo_path: PosixPath) -> None:
        if not repo_path.exists():
            sys.stderr.write("There's no real path")
        if subprocess.Popen(['git', 'fetch'], cwd=repo_path).returncode != 0:
            sys.stderr.write("There's no git repository") 
            return 

    def __check_pid_file(self) -> bool:
        """return true if file exists"""
        return Path(self.pidfile).is_file()

    def __get_pid(self) -> int | None:
        """return pid from pidfile"""
        if not self.__check_pid_file():
            sys.stderr.write(f"pidfile is not found\n")
            return None

        with Path(self.pidfile).open() as pidfile:
            pid = int(pidfile.readline())

        return pid

    def start(self) -> None:
        if self.__check_pid_file():
            pid = self.__get_pid()
            sys.stdout.write(f"process {pid} already started!!!\n")
            sys.exit()
        
        self.daemonize()
        self.run()


    def stop(self) -> None:
        pid = self.__get_pid()
        if pid is None:
            sys.stdout.write(f"process not started!!!\n")
            sys.exit()

        os.kill(pid, signal.SIGTERM)
        sys.stdout.write(f"process {pid} stopped!!!")
        sys.stdout.flush()
        os.remove(self.pidfile)

    def status(self):
        if not self.__check_pid_file():
            sys.stdout.write(f"process not started!!!\n")
            sys.exit()

        pid = self.__get_pid()
        sys.stdout.write(f"proccess {pid} running")

    def fetch(self) -> None:
        subprocess.run(['git', 'fetch'])

    def run(self) -> None:
        while True:
            time.sleep(1)

