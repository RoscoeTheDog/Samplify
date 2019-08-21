from datetime import datetime
import platform
import os


def is_between(current, date_start, date_end):

    if date_start <= current <= date_end:
        return True

    else:
        return False


def created(path):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """

    # TODO: Test this code block on other platforms (OS X/Linux)

    if platform.system() == 'Windows':
        date = datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d')
        return date

    else:
        stat = os.stat(path)

        try:
            return stat.st_birthtime

        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime