#!/usr/bin/python3
# Fabfile to create and distribute an archive to web servers.
from fabric.api import env, local, run, put
from datetime import datetime
from os.path import isfile
from pathlib import Path

env.hosts = ["54.173.251.99", "52.91.125.177"]
env.user = "ubuntu"
env.key_filename = "~/.ssh/0-use_a_private_key"

def do_pack():
    """Create a tar gzipped archive of the directory web_static."""
    try:
        dt = datetime.utcnow()
        file = "versions/web_static_{}{}{}{}{}{}.tgz".format(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
        )
        if not Path("versions").is_dir():
            local("mkdir -p versions")
        result = local("tar -cvzf {} web_static".format(file))
        return file if result.succeeded else None
    except Exception as e:
        print(e)
        return None

def do_deploy(archive_path):
    """Distribute an archive to web servers.

    Args:
        archive_path (str): The path of the archive to distribute.
    Returns:
        If the file doesn't exist at archive_path or an error occurs - False.
        Otherwise - True.
    """
    if not isfile(archive_path):
        return False

    file = Path(archive_path).name
    name = file.split(".")[0]

    remote_tmp = "/tmp/{}".format(file)
    remote_release = "/data/web_static/releases/{}/".format(name)

    try:
        # Upload the archive to /tmp/ directory of the web server
        put(archive_path, remote_tmp)

        # Create a new release directory
        run('mkdir -p {}'.format(remote_release))

        # Extract the archive to the new release directory
        run('tar -xzf {} -C {}'.format(remote_tmp, remote_release))

        # Remove the uploaded archive from /tmp/
        run('rm {}'.format(remote_tmp))

        # Move contents to the release directory
        run('mv {}web_static/* {}'.format(remote_release, remote_release))

        # Remove unnecessary web_static directory
        run('rm -rf {}web_static'.format(remote_release))

        # Remove the current symbolic link
        run('rm -rf /data/web_static/current')

        # Create a new symbolic link
        run('ln -s {} /data/web_static/current'.format(remote_release))

        return True
    except Exception as e:
        print(e)
        return False

def deploy():
    """Create and distribute an archive to web servers."""
    archive_path = do_pack()
    if not archive_path:
        return False
    return do_deploy(archive_path)
