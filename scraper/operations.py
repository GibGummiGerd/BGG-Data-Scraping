from datetime import datetime
import unicodedata
import os
import re
import time
import requests
import numpy


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "_", value).strip("-_")


def check_path_for_file_name_with_substring(
    string_to_check: str, relative_path: str
) -> bool:
    """Checks if a file with a given substring exists in a directory.

    Args:
        string_to_check (str): Substring which is searched for in file names.
        relative_path (str): Relative path to folder which is searched.

    Returns:
        bool: True is a file with substring in name exists.
    """
    list_of_files = os.listdir(relative_path)
    for file in list_of_files:
        if string_to_check in file:
            return True
    return False


def get_request(url: str) -> requests.Response:
    """_summary_

    Args:
        url (str): _description_

    Raises:
        SystemExit: _description_
        SystemExit: _description_
        SystemExit: _description_

    Returns:
        requests.Response: _description_
    """

    sleep_time = 0

    while True:
        try:
            get_response = requests.get(url)
        except requests.exceptions.Timeout:
            sleep_time += 1
            print(f"Request timed out. Will wait {sleep_time} seconds and try again")
            time.sleep(sleep_time)
        except requests.exceptions.TooManyRedirects as err:
            raise SystemExit(err) from err
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err) from err
        except requests.exceptions.RequestException as err:
            raise SystemExit(err) from err

        break

    return get_response


def later_date(date1, date2):

    if isinstance(date1, str):
        str_to_time(date1)
    elif not isinstance(date1, datetime):
        date1 = numpy.nan
    if isinstance(date2, str):
        str_to_time(date2)
    elif not isinstance(date2, datetime):
        date2 = numpy.nan

    if date1 == date2:
        return date1
    if date1 is numpy.nan:
        return date2
    if date2 is numpy.nan:
        return date1
    if date1 > date2:
        return date1
    return date2


def str_to_time(date: str) -> datetime:

    if not isinstance(date, str):
        return numpy.nan

    return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
