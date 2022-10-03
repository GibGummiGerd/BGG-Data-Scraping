import os
import re
import pandas
from datetime import date

from const import *
from operations import *


def find_csv_by_id(IDs: list[str]) -> dict:

    matches = {}
    files = os.listdir(CSV_FOLDER)

    for game_id in IDs:
        for file in files:
            if does_file_name_start_with_id(game_id, file):
                matches[game_id] = file
                break

    return matches


def does_file_name_start_with_id(game_id, file_name):
    regex_underscore = f"^{game_id}_"
    regex_dash = f"^{game_id}-"
    return re.match(regex_underscore, file_name) or re.match(regex_dash, file_name)


def open_csv_by_name(file_name):

    filepath = os.path.join(CSV_FOLDER, file_name)
    return pandas.read_csv(filepath)


def delete_progress_file(game_id: str):
    os.remove(create_progress_path(game_id))


def create_progress_path(game_id: str) -> str:
    return os.path.join(PROGRESS_FOLDER, f"{game_id}_progress.json")


def create_csv_folder_path_from_filename(filename):
    return os.path.join(CSV_FOLDER, filename)


def create_csv_file_name_with_date(game_id, game_name):
    game_name = slugify(game_name)
    filename_parts = [f"{game_id}", game_name, str(date.today())]
    filename = "_".join(filename_parts) + ".csv"
    return filename


def create_csv_folder_path_from_id_and_name(game_id, game_name):
    filename = create_csv_file_name_with_date(game_id, game_name)
    return create_csv_folder_path_from_filename(filename)
