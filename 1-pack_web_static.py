#!/usr/bin/python3
from fabric.api import local
from datetime import datetime
import os


def do_pack():
    """
    Generate a .tgz archive from the contents of the web_static folder.

    Returns:
        (str): Path to the generated archive, or None if unsuccessful.
    """
    # Create the 'versions' folder if it doesn't exist
    local("mkdir -p versions")

    # Get the current date and time
    now = datetime.now()
    date_string = now.strftime("%Y%m%d%H%M%S")

    # Set the filename for the archive
    archive_name = f"web_static_{date_string}.tgz"

    # Compress the web_static folder into the archive
    result = local(f"tar -czvf versions/{archive_name} web_static")

    if result.succeeded:
        return os.path.abspath(f"versions/{archive_name}")
    else:
        return None
