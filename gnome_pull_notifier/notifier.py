from collections.abc import Mapping
from pathlib import PosixPath, Path
from gnome_pull_notifier.daemon import Daemon
import time
import sys
import signal
import os

import gi

from gnome_pull_notifier.errors import GitRepoPathNotFound # type: ignore
gi.require_version('Notify', '0.7')

from gi.repository import Notify
from typing import Any, Dict

from typing import Sequence

import subprocess

PIDFILE_LOCATION = "/tmp/git-notifier.pid"

CONFIG_PATH = Path("~/.config/gitnotifier").expanduser()
REPO_LIST_PATH = CONFIG_PATH / "repolist"

class GitNotifier(Daemon):

    def __init__(self, *args: Sequence[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
    
    def __save_repo(self, *repos: str) -> None:
        with REPO_LIST_PATH.resolve().open(mode="w+") as repolist:
            repolist.writelines(repos)

    def add_repo(self, repo_path: PosixPath) -> None:
        path = repo_path.expanduser().absolute()
        if not path.exists():
            sys.stderr.write("There's no real path: {path}\n")
            raise GitRepoPathNotFound
        if not (path / ".git").exists():
            sys.stderr.write("There's no git repository\n") 
            return 
        self.__save_repo(str(path))

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
        sys.stdout.write(f"process {pid} stopped!!!\n")
        sys.stdout.flush()
        os.remove(self.pidfile)

    def status(self):
        if not self.__check_pid_file():
            sys.stdout.write(f"process not started!!!\n")
            sys.exit()

        pid = self.__get_pid()
        sys.stdout.write(f"proccess {pid} running:\n")
        sys.stdout.write(f"\trepo list path:{REPO_LIST_PATH}\n")
        sys.stdout.write(f"\trepo list:\n")
        try:
            with REPO_LIST_PATH.open(mode="r+") as repolist:
                for repo in repolist.readlines():
                    sys.stdout.write(f"\t\t{repo}\n")
        except FileNotFoundError:
            sys.stdout.write("repo list not found!!!")

    def fetch(self) -> None:
        subprocess.run(['git', 'fetch'])

    def run(self) -> None:
        while True:
            time.sleep(1)

