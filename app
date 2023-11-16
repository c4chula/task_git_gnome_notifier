#!/usr/bin/env python

from gnome_pull_notifier.notifier import GitNotifier
from gnome_pull_notifier.dispatcher import dispatcher 

PIDFILE_LOCATION = "/tmp/git-notifier.pid"

def main():
    daemon = GitNotifier(PIDFILE_LOCATION)
    dispatcher(daemon)

if __name__ == "__main__":
    main()
