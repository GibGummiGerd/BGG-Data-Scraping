import json
import os
from pathlib import Path
import pandas
import operations

PROGRESS_FOLDER = "progress"
PROGRESS_ID = "id"
PROGRESS_PAGE = "page"
PROGRESS_RATING = "rating"

CSV_FOLDER = "csv"

FINISHED_FILE = "finished.txt"


def create_list_of_rating_items(user_item_bytes: bytes) -> list:

    user_items = list()

    for user_item in user_item_bytes["items"]:

        comment: str = user_item["textfield"]["comment"]["value"]
        if comment is not None:
            comment = comment.strip().replace("\n", " ")

        status = user_item["status"]
        own = False
        prevowned = False
        wishlist = False
        for key in status:
            match key:
                case "own":
                    own = True
                case "prevowned":
                    prevowned = True
                case "wishlist":
                    wishlist = True

        user_item = {
            "rating": user_item["rating"],
            "username": user_item["user"]["username"],
            "country": user_item["user"]["country"],
            "own": own,
            "prevowned": prevowned,
            "wishlist": wishlist,
            "textfield": comment,
            "rating_tstamp": user_item["rating_tstamp"],
            "comment_tstamp": user_item["comment_tstamp"],
        }
        user_items.append(user_item)

    return user_items


def save_progress(game_id: str, page_counter: str):

    Path(PROGRESS_FOLDER).mkdir(parents=True, exist_ok=True)

    progress = {
        PROGRESS_ID: game_id,
        PROGRESS_PAGE: page_counter,
        PROGRESS_RATING: page_counter * 50,
    }

    with open(create_progress_path(game_id), "w", encoding="utf-8") as temp_file:
        temp_file.write(json.dumps(progress))

    return


def save_rating_item(dict_list: list[dict], output_path: str):

    Path(CSV_FOLDER).mkdir(parents=True, exist_ok=True)

    pandas.DataFrame(dict_list).to_csv(
        output_path, mode="a", header=not os.path.exists(output_path), index=False
    )


def delete_progress_file(game_id: str):
    os.remove(create_progress_path(game_id))


def create_progress_path(game_id: str) -> str:
    return os.path.join(PROGRESS_FOLDER, f"{game_id}_progress.json")


def create_rating_items_path(game_id: str, game_name: str):

    game_name = operations.slugify(game_name)

    return os.path.join(CSV_FOLDER, f"{game_id}_{game_name}_rating_items.csv")


def remove_duplicates_from_csv(filepath: str):

    data_frame = pandas.read_csv(filepath)
    data_frame = data_frame.drop_duplicates()
    data_frame.to_csv(filepath, mode="w", header=True, index=False)


def get_unfinished_games() -> list[dict]:

    list_of_unfinished_games = []

    if not os.path.exists(PROGRESS_FOLDER):
        print(f"Directory {PROGRESS_FOLDER} does not exist")
        return []

    for filename in os.listdir(PROGRESS_FOLDER):
        if "progress" not in filename:
            continue
        print("want " + filename)
        with open(
            os.path.join(PROGRESS_FOLDER, filename), "r", encoding="utf-8"
        ) as opened_file:
            list_of_top_games = json.load(opened_file)
            list_of_unfinished_games.append(list_of_top_games)

    return list_of_unfinished_games


def add_game_to_finished(game_id: str):
    with open(
        os.path.join(PROGRESS_FOLDER, FINISHED_FILE), "a", encoding="utf-8"
    ) as finished_file:
        finished_file.write(f"{game_id}\n")
