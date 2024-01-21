#!/usr/bin/python3
# Fabfile to deploy an archive to web servers.
from fabric.api import env, put, run
from os.path import exists
from datetime import datetime

env.hosts = ["54.173.251.99", "52.91.125.177"]
env.user = "ubuntu"
env.key_filename = "~/.ssh/0-use_a_private_key"

def do_pack():
    """Create a tar gzipped archive of the directory web_static."""
    dt = datetime.utcnow()
    file = "versions/web_static_{}{}{}{}{}{}.tgz".format(dt.year,
            dt.month, dt.day, dt.hour, dt.minute, dt.second)

    # Ensure the versions directory exists
    with settings(warn_only=True):
        local("mkdir -p versions")

    # Create the .tgz archive
    result = local("tar -cvzf {} web_static".format(file))

    if result.failed:
        return None

    return file

def do_deploy(archive_path):
    """
    Distributes an archive to web servers

    Args:
        archive_path (str): Path to the archive to be deployed

    Returns:
        True if all operations have been done correctly, otherwise False
    """
    if not exists(archive_path):
        return False

    try:
        archive_name = archive_path.split("/")[-1]
        archive_no_ext = archive_name.split(".")[0]

        # Upload archive to /tmp/ directory of the web server
        put(archive_path, "/tmp/")

        # Create the release directory
        run("mkdir -p /data/web_static/releases/{}".format(archive_no_ext))

        # Uncompress the archive to the release directory
        run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/"
            .format(archive_name, archive_no_ext))

        # Remove the uploaded archive
        run("rm /tmp/{}".format(archive_name))

        # Move files to the final destination
        run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/"
            .format(archive_no_ext, archive_no_ext))

        # Remove the web_static directory
        run("rm -rf /data/web_static/releases/{}/web_static".format(archive_no_ext))

        # Remove the current symbolic link
        run("rm -rf /data/web_static/current")

        # Create a new symbolic link
        run("ln -s /data/web_static/releases/{}/ /data/web_static/current"
            .format(archive_no_ext))

        print("New version deployed!")
        return True
    except Exception as e:
        print(e)
        return False
