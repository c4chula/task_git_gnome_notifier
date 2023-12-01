from pathlib import PosixPath, Path
from gnome_pull_notifier.daemon import Daemon
import time
import sys
import signal
import os


from gnome_pull_notifier.errors import GitRepoPathNotFound
import gi
gi.require_version('Notify', '0.7')

from gi.repository import Notify 
from typing import Any, Dict

from typing import Sequence, List
import logging


import subprocess

PIDFILE_LOCATION = Path("/tmp/git-notifier.pid")

CONFIG_PATH = Path("~/.config/gitnotifier").expanduser().absolute()
REPO_LIST_PATH = CONFIG_PATH / "repolist"
LOG_PATH = CONFIG_PATH / "logs.log"

CONFIG_PATH.mkdir(parents=True, exist_ok=True)
REPO_LIST_PATH.touch(exist_ok=True)
LOG_PATH.touch(exist_ok=True)
DEFAULT_BRANCH="main"

TIME_AWAIT_S = 15 

Notify.init("Git Pull Notifier")
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG)

class GitNotifier(Daemon):

    def __init__(self, *args: Sequence[Any], **kwargs: Dict[str, Any]) -> None:
        self.__repo_list = self.__get_repo_list()
        super().__init__(*args, **kwargs)
   
    def __get_repo_list(self) -> List[PosixPath]:
        repos: List[PosixPath]
        with REPO_LIST_PATH.open() as repolist:
            repos = [PosixPath(path) for path in repolist.readlines()]
        return repos

    def __save_repo(self, *repos: str) -> None:
        with REPO_LIST_PATH.resolve().open(mode="a+") as repolist:
            for repo in repos:
                repolist.write(f"{repo}")

    def add_repo(self, repo_path: PosixPath) -> None:
        path = repo_path.expanduser().absolute()
        if not path.exists():
            sys.stderr.write("There's no real path: {path}\n")
            raise GitRepoPathNotFound
        if not (path / ".git").exists():
            sys.stderr.write("There's no git repository\n") 
            return 
        self.__save_repo(str(path))
        self.__repo_list = self.__get_repo_list()

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

    def __check_pid(self, pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

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

    def status(self) -> None:
        if not self.__check_pid_file():
            sys.stdout.write(f"process not started!!!\n")
            sys.exit()

        pid = self.__get_pid()

        if pid is None:
            sys.stderr.write(f"pid of daemon not found!!!\n")
            return

        if not self.__check_pid(pid):
            sys.stderr.write(f"proccess not found!!! removing pidfile")
            PIDFILE_LOCATION.unlink(missing_ok=True)

            
        sys.stdout.write(f"proccess {pid} running:\n")
        sys.stdout.write(f"\trepo list path:{REPO_LIST_PATH}\n")
        sys.stdout.write(f"\trepo list:\n")
        try:
            for repo in self.__get_repo_list():
                sys.stdout.write(f"\t\t{repo}\n")
        except FileNotFoundError:
            sys.stdout.write("repo list not found!!!\n")

    def __get_fetch(self, repo_path: PosixPath) -> None:
        ps = subprocess.Popen(
            [
                "git",
                "fetch",
            ],
            cwd=repo_path,
        )
        ps.wait()


    def __get_log_info(self, repo_path: PosixPath) -> str | None:
        ps = subprocess.Popen(
            [
                "git",
                "log",
                "--graph",
                "--pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr)%Creset'",
                "--abbrev-commit",
                "--date=relative",
                f"{DEFAULT_BRANCH}..origin/{DEFAULT_BRANCH}",
            ],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            text=True,
            env= {
                "PAGER": "cat",
            }
        )
        ps.wait()
        output, _ = ps.communicate()
        if output == "":
            return None
        return str(output)

    def run(self) -> None:
        while True:
            for repo in self.__repo_list:
                self.__get_fetch(repo)
                message = self.__get_log_info(repo)
                logging.debug(f"got log info: {message}")        
                if message is not None: 
                    Notify.Notification.new(message).show()
            time.sleep(TIME_AWAIT_S)
