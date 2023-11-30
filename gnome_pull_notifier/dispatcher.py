from pathlib import Path, PosixPath 
from gnome_pull_notifier.notifier import GitNotifier
import sys

def dispatcher(daemon: GitNotifier) -> None:
    match sys.argv[1:]:
        case ["start", *_]:
            daemon.start()
        case ["restart", *_]:
            daemon.restart()
        case ["stop", *_]:
            daemon.stop()
        case ["status", *_]:
            daemon.status()
        case ["add", repo, *_]:
            daemon.add_repo(PosixPath(repo))
