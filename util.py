import os
import json
from shutil import copyfile

TEMP_PATH = 'temp'
LOGS_PATH = 'logs'


def profiles_db_copy(browser: dict, file_name: str) -> list[str]:
    """ Create temporary instances of file_name for each profile and return their new names """
    temp_names = []
    # Examine each profile
    for subdir_name in os.listdir(browser['path']):
        if subdir_name == 'Default' or subdir_name.startswith('Profile'):
            # Copy original sqlite3 database to access it without killing any active Chrome processes
            original_path = f"{browser['path']}\\{subdir_name}\\{file_name}"
            temp_name = f"{browser['name']} {subdir_name} {file_name}"
            temp_path = f'{TEMP_PATH}\\{temp_name}'
            copyfile(original_path, temp_path)
            temp_names.append(temp_name)
    return temp_names

def log_file(data: dict, file_name: str) -> None:
    """ Create log for file_name """
    log_path = f'{LOGS_PATH}\\{file_name}.json'
    with open(log_path, 'w') as f:
        json.dump(data, f, indent=4)


