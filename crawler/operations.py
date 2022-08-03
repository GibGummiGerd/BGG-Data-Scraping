import unicodedata
import os
import re


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
