#!/usr/bin/python3
# Fabfile to delete out-of-date archives.
import os
from fabric.api import *

env.hosts = ["54.173.251.99", "52.91.125.177"]
env.user = "ubuntu"
env.key_filename = "~/.ssh/0-use_a_private_key"

def do_clean(number=0):
    """Delete out-of-date archives.

    Args:
        number (int): The number of archives to keep.

    If number is 0 or 1, keeps only the most recent archive. If
    number is 2, keeps the most and second-most recent archives,
    etc.
    """
    number = 1 if int(number) == 0 else int(number)

    with lcd("versions"):
        local("ls -t | tail -n +{} | xargs rm -f".format(number + 1))

    with cd("/data/web_static/releases"):
        run("ls -tr | grep web_static | tail -n +{} | xargs rm -rf".format(number + 1))
