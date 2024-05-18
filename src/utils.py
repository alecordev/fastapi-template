import os
import re
import sys
import base64
import hashlib
import config
import logging
import inspect
import linecache
import traceback
import datetime
import secrets

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def log(msg):
    print(f"[{now().isoformat()}] {msg}")


def get_exception_details(num=-1):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    exception_string = "".join(traceback.format_exception_only(exc_type, exc_value))
    (filename, line_number, function_name, text) = traceback.extract_tb(exc_traceback)[
        num
    ]

    calling_frame = inspect.getframeinfo(inspect.currentframe().f_back)
    calling_function = calling_frame.function
    calling_line_number = calling_frame.lineno

    prev_line_number = max(1, line_number - 1)
    prev_line_code = linecache.getline(filename, prev_line_number).strip()
    error = {
        "type": str(exc_type.__name__),
        "value": str(exc_value),
        "message": exception_string,
        "location": {
            "filename": filename,
            "lineno": line_number,
            "function_name": function_name,
            "line": text,
        },
        "previous_call": {
            "line_number": prev_line_number,
            "code": prev_line_code,
        },
        "calling_function": calling_function,
        "calling_line_number": calling_line_number,
    }
    return error


def make_token(length=8):
    return secrets.token_hex(length)


def generate_hash(password=None, salt=None):
    """
    Generates a salted hash from a password.

    Helps create new users.

    Args:
        password (str): Password to hash.
        salt (str): Salt string.

    Returns:
        str
    """
    if not password:
        raise Exception("Password needs to be provided.")
    if not salt:
        salt = secrets.token_bytes(32)
    hashed_password = hashlib.pbkdf2_hmac("sha512", password.encode(), salt, 1000000)
    return "{impl}${iterations}${salt}${pwd}".format(
        impl="pbkdf2_hmac_sha512",
        iterations=1000000,
        salt=base64.b64encode(salt).decode(),
        pwd=base64.b64encode(hashed_password).decode(),
    )


def authenticate(user, password):
    """
    Authenticates a user:password combination.

    Args:
        user (str): Username
        password (str): Password

    Returns:
        bool - True if successfully authenticated
    """
    credentials = {
        "user": "pbkdf2_hmac_sha512$100000$YDY2TfhkmEfHh9V7zGjJCfryaruZsem42G5vKj4AZGk=$OL28maKhn8pRKBo6sudQA4L0PSQ2pOSYLoerYRnPY+/ifKzWqbkFB6BHWIxtddg6BTANqhkKuyTGoCVe/N7pCA==",
    }
    if user in credentials:
        hashed_password = credentials.get(user)
        salt = hashed_password.split("$")[2]
        return (
            generate_hash(password=password, salt=base64.b64decode(salt))
            == hashed_password
        )
    else:
        return False


def add_to_system_path(directory):
    p = os.environ.get("PATH", "")
    path = f"{directory}:{p}"
    os.environ["PATH"] = path


def add_to_python_path(directory):
    sys.path.append(directory)


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS)
