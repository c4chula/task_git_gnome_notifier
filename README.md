# task_git_gnome_notifier
daemon process (UNIX double fork mechanism) which creates GNOME notifications of new changes on origin/HEAD branch of repo

Activate virtual enviroment
```bash
python -m venv venv
source ./venv/bin/activate
```

First you need to load depencies via poetry:
```bash
poetry install
```

Make executable main python file:
```bash
chmod +x app
```

After you can use commands
```bash
./app start # Start the daemon
./app stop # Stop the daemon
./app status # get status of daemon
```

`status` command also show using list of git repos. You can add repo via command `add`:
```bash
./app add path/to/repo
```

All paths stores in user config for gitnotifier `~/,config/gitnotifier/repolist` (Creates automatically)
