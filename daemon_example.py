from collections.abc import Mapping
from pathlib import PosixPath
from daemon import Daemon
import time
import sys

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

from typing import Sequence

import subprocess

class MyDaemon(Daemon):

    def __init__(self, *args, **kwargs) -> None:
        self.repo_paths: Mapping[str,PosixPath] = {} 
        super().__init__(*args, **kwargs)

    def add_repo(self, repo_path: PosixPath) -> None:
        if not repo_path.exists():
            sys.stderr.write("There's no real path")
        if (p := subprocess.Popen(['git', 'fetch'], cwd=repo_path)).returncode != 0:
            sys.stderr.write("There's no git repository") 
            return 

    def __check_pid_file(self):
        """return true if file exists"""
        return Path(self.pidfile).is_file()

    def __get_pid(self):
        """return pid from pidfile"""
        if not self.__check_pid_file():
            sys.stderr.write(f"pidfile is not found\n")
            return None

        with Path(self.pidfile).open() as pidfile:
            pid = int(pidfile.readline())

        return pid

    def __warn_exist_pid(self, pid):
        sys.stdout.write(f"process {pid} already started!!!\n")

    def __warn_non_exist_pid(self):
        sys.stdout.write(f"process not started!!!\n")

    def start(self):
        if self.__check_pid_file():
            pid = self.__get_pid()
            self.__warn_exist_pid(pid)
            sys.exit()
        
        self.daemonize()
        self.run()


    def stop(self):
        pid = self.__get_pid()
        if pid is None:
            self.__warn_non_exist_pid()
            sys.exit()

        os.kill(pid, signal.SIGTERM)
        sys.stdout.write(f"process {pid} stopped!!!")
        sys.stdout.flush()
        os.remove(self.pidfile)

    def status(self):
        if not self.__check_pid_file():
            self.__warn_non_exist_pid()
            sys.exit()

        pid = self.__get_pid()
        sys.stdout.write(f"proccess {pid} running")

    def fetch(self) -> None:
        subprocess.run(['git', 'fetch'])

    def run(self) -> None:
        while True:
            time.sleep(1)

def dispatcher(daemon, op, *args) -> None:
    match op:
        case "start":
            daemon.start()
        case "restart":
            daemon.restart()
        case "stop":
            daemon.stop()
        case "status":
            daemon.status()


def main():
    _, pidfile, op, *args = sys.argv
    daemon = MyDaemon(pidfile)
    dispatcher(daemon, op, *args)


if __name__ == "__main__":
    main()
