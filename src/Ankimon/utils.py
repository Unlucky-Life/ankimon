import os
import requests

def check_folders_exist(parent_directory, folder):
    folder_path = os.path.join(parent_directory, folder)
    return os.path.isdir(folder_path)

def check_file_exists(folder, filename):
    file_path = os.path.join(folder, filename)
    return os.path.isfile(file_path)

def test_online_connectivity(url='https://raw.githubusercontent.com/Unlucky-Life/ankimon/main/update_txt.md', timeout=5):
    try:
        # Attempt to get the URL
        response = requests.get(url, timeout=timeout)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            return True
    except:
        # Connection error means no internet connectivity
        return False