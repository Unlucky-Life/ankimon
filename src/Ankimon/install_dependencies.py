import subprocess
import sys
import os
from aqt.utils import tooltip, showInfo
import site

def install_package(package_name):
    """Attempt to install a package using pip locally and handle failures."""
    try:
        # Get the directory where the current script is located
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Define the local lib directory where dependencies will be installed
        lib_dir = os.path.join(script_dir, "lib")

        # Make sure the lib directory exists
        if not os.path.exists(lib_dir):
            os.makedirs(lib_dir)

        # Install the package to the local directory
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name, "--target", lib_dir],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Add the local lib directory to sys.path
        sys.path.append(lib_dir)

        if result.returncode == 0:
            tooltip(f"Successfully installed {package_name} to {lib_dir}")
            # Optionally, show installed packages' site directories
            # showInfo(f"Packages installed at: {site.getsitepackages()}")
        else:
            tooltip(f"Failed to install {package_name}. Error: {result.stderr}")
    except subprocess.CalledProcessError as e:
        tooltip(f"Failed to install {package_name}. Error: {e}")
    except Exception as e:
        tooltip(f"An unexpected error occurred: {e}")
