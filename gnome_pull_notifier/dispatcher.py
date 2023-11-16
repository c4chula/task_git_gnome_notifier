from gnome_pull_notifier.notifier import GitNotifier
import sys

def dispatcher(daemon: GitNotifier) -> None:
    match sys.argv[1:]:
        case ["start", *args]:
            daemon.start()
        case ["restart", *args]:
            daemon.restart()
        case ["stop", *args]:
            daemon.stop()
        case ["status", *args]:
            daemon.status()
