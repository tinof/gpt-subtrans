import os
import sys

import appdirs


try:
    from importlib.resources import files
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files

config_dir = appdirs.user_config_dir("GPTSubtrans", "MachineWrapped", roaming=True)


def GetResourcePath(relative_path, *parts):
    """
    Locate a resource file or folder in the application package or development directory.
    """
    if hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path, *parts)

    try:
        # Try to get resource from the installed package
        resource_path = files("PySubtitle").joinpath(relative_path)
        if parts:
            for part in parts:
                resource_path = resource_path.joinpath(part)
        return str(resource_path)
    except (ModuleNotFoundError, FileNotFoundError, AttributeError):
        # Fallback for development mode - look relative to current working directory
        return os.path.join(os.path.abspath("."), relative_path or "", *parts)
