#!/usr/bin/env python3

"""bgg.py"""

from datetime import datetime
import time
import os
import json
import argparse
import sys
import pandas

import bgg
import data
import update_games
from const import *


def collect_ratings(game_id: str, page_counter: int = 1):

    game_info = bgg.find_game_info(game_id)

    game_name = game_info["name"]
    estimated_ratings = game_info["voters"] * 1.03

    output_path = data.create_rating_items_path(game_id, game_name)

    sleep_time = SLEEP_TIME
    start_time = datetime.now()
    fail_counter = 1

    while fail_counter < MAX_FAILS:

        # sleep to stay under the request limit
        time.sleep(sleep_time)

        json_bytes, ok = bgg.rating_request(game_id, page_counter)
        if not ok:
            sleep_time = sleep_time + 0.1
            fail_counter = fail_counter + 1
            # wait to not directly run into request limit again
            time.sleep(5)
            continue

        user_dict_list = data.create_list_of_rating_items(json_bytes)

        estimated_time = (estimated_ratings / 50 - page_counter) * sleep_time
        estimated_min = int(estimated_time // 60)
        estimated_sec = int((estimated_time / 60) % 1 * 60)

        if len(user_dict_list) == 0:
            print("Reached last ratings \n--END FLOW--")
            break

        data.save_rating_item(user_dict_list, output_path)
        data.save_progress(game_id, page_counter)

        print(
            ". . . . . . . . . . .\n"
            + f"Game: {game_name} (ID: {game_id}) \nCurrent run time: "
            + str(datetime.now() - start_time)
            + f"; one request every {sleep_time} seconds"
            + f"\nPage: {page_counter} \nCollected Ratings: "
            + str(page_counter * 50)
            + f"\nEstimated ratings: {int(estimated_ratings)}"
            + f"\nEstimated remaining time: {estimated_min} min {estimated_sec} sec"
        )

        page_counter += 1
        fail_counter = 0

    if fail_counter >= MAX_FAILS:
        print(f"Failed {MAX_FAILS} times in  a row to get a request. Ending process.")
        sys.exit()

    data.add_game_to_finished(game_id)
    data.delete_progress_file(game_id)

    return


def complete_games():

    unfinished_games = data.get_unfinished_games()
    for game in unfinished_games:
        game_id = game[PROGRESS_ID]
        collect_ratings(game_id, page_counter=game[PROGRESS_PAGE])

        print("now remove duplicates")

        game_name = bgg.find_game_name(game_id)
        filepath = data.create_rating_items_path(game_id, game_name)
        data.remove_duplicates_from_csv(filepath)

    return


def main():

    parser = argparse.ArgumentParser()

    # -db DATABSE -u USERNAME -p PASSWORD -size 20
    parser.add_argument(
        "-c",
        "--complete",
        dest="complete",
        help="Set if you want to complete unfinished games",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-i",
        "--id",
        dest="id",
        help="Set if you want to get a specific game",
        type=int,
        default=0,
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        help="Set if you want to get a specific game",
        type=str,
    )
    parser.add_argument(
        "-u",
        "--update",
        dest="update",
        help="Update existing files in csv folder with new ratings",
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()

    if args.complete is True:
        complete_games()
        return

    if args.id > 0:
        collect_ratings(args.id)
        return

    ranking_file = args.file

    if ranking_file == "":
        print("No file given which specifies which ids are to be collected")
        sys.exit()

    ids_to_be_collected = []

    try:
        if ranking_file.lower().endswith(".txt"):
            with open(ranking_file, "r", encoding="utf-8") as f:
                for line in f:
                    ids_to_be_collected.append(line.strip().lstrip().rstrip())
        elif ranking_file.lower().endswith(".csv"):
            data_frame = pandas.read_csv(ranking_file)
            ids_to_be_collected = data_frame["ID"].to_list()
    except Exception as err:
        print(err)
        sys.exit()

    if args.update is True:
        print(ids_to_be_collected)
        update_games.update_games(ids_to_be_collected)
        return

    collected_games = []
    try:
        collected_games = os.listdir(CSV_FOLDER)
    except FileNotFoundError:
        os.mkdir(CSV_FOLDER)

    for game_id in ids_to_be_collected:

        # Check if we already have a csv file starting with the id
        if any(game_id == csv_file.split("_")[0] for csv_file in collected_games):
            print(f"Already have game with id {game_id}")
            continue
        print(f"Will now collect game with id {game_id}")

        collect_ratings(game_id)

        # further = input("Continue? Just hit Enter")
        # if further != "":
        #     break


if __name__ == "__main__":
    main()
