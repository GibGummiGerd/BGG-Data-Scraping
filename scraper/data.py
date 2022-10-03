import json
import os
from pathlib import Path
import pandas
import operations

from const import *
from files import *


def create_list_of_rating_items(user_item_bytes: bytes) -> list:

    user_items = list()

    for user_item in user_item_bytes["items"]:

        comment: str = user_item["textfield"]["comment"]["value"]
        if comment is not None:
            comment = comment.strip().replace("\n", " ").replace("\r", " ")

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
            "comment": comment,
            "rating_tstamp": user_item["rating_tstamp"],
            "comment_tstamp": user_item["comment_tstamp"],
            "review_tstamp": user_item["review_tstamp"],
            "postdate": user_item["postdate"],
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


def save_rating_item_dict(dict_list: list[dict], output_path: str, write_mode="a"):

    Path(CSV_FOLDER).mkdir(parents=True, exist_ok=True)

    data_frame = pandas.DataFrame(dict_list)
    data_frame = remove_bad_data(data_frame)

    data_frame.to_csv(
        output_path,
        mode=write_mode,
        # if write mode is w, a header will be cerated
        header=not os.path.isfile(output_path),
        index=False,
    )


def remove_duplicates_from_csv(filepath: str):

    data_frame = pandas.read_csv(filepath)
    data_frame.sort_values(by=LATEST_TSTAMP, inplace=True, ascending=False)
    data_frame.reset_index(drop=True, inplace=True)
    data_frame.drop_duplicates(subset=[USERNAME], inplace=True, keep="first")
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


def create_latest_tstamp_column(row):
    return operations.later_date(row[RATING_DATETIME], row[COMMENT_DATETIME])


def remove_bad_data(data_frame: pandas.DataFrame):
    data_frame.drop(
        data_frame.loc[
            (data_frame[RATING_DATETIME] == "0000-00-00 00:00:00")
            & (data_frame[COMMENT_DATETIME] == "0000-00-00 00:00:00")
        ].index,
        inplace=True,
    )
    data_frame.replace(
        {
            RATING_DATETIME: "0000-00-00 00:00:00",
            COMMENT_DATETIME: "0000-00-00 00:00:00",
        },
        numpy.nan,
        inplace=True,
    )
    return data_frame
