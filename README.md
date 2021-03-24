# Krwm Tools

A tool for extracting sensitive data from Chromium browsers on Windows. Able to extract:
- Passwords
- Autofill fields
- Autofill profiles
- Autofill addresses
- Autofill names
- Autofill emails
- Autofill phone numbers
- Credit card info
- Cookies
- History (search terms and web history)


## Setup
**Option 1**: Download krwmtools-win from Releases (on the right). Extract and run the containing krwmtools.exe file.

**Option 2**: Directly with python
1. Make sure you are in the root directory of the repo.
1. Install dependencies with `pip install -r .\src\requirements.txt`.
1. Start the program with `python .\src\main.py`.

Extracted data will be placed in your `Documents\Krwm Tools\logs` directory.


## Disclaimer
This tool was made for educational purposes (for a university project). Please do not use it on others illegally or without their explicit consent, and note that I am not responsible for any damage.
