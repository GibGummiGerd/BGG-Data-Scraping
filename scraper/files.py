import os
import re
import pandas

from const import *


def find_csv_by_id(IDs: list[str]) -> dict:

    matches = {}
    files = os.listdir(CSV_FOLDER)

    for game_id in IDs:
        regex = f"^{game_id}_"
        for file in files:
            if re.match(regex, file):
                matches[game_id] = file
                break

    return matches


def open_csv_by_name(file_name):

    filepath = os.path.join(CSV_FOLDER, file_name)
    return pandas.read_csv(filepath)
