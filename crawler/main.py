"""bgg.py"""

from datetime import datetime
from pathlib import Path
import time
import os
import json
import argparse

import bgg
import data


def collect_ratings(game_id: str, page_counter: int = 1):

    game_info = bgg.find_game_info(game_id)

    game_name = game_info["name"]
    estimated_ratings = game_info["voters"] * 1.03

    output_path = data.create_rating_items_path(game_id, game_name)

    sleep_time = 3.8
    start_time = datetime.now()
    fail_counter = 1

    while fail_counter < 10:

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

    if fail_counter >= 10:
        with open(output_path, "a", encoding="utf-8") as csv_file:
            csv_file.write("Did not get all the data\n")
        return

    data.add_game_to_finished(game_id)
    data.delete_progress_file(game_id)

    return


def finish_games():

    unfinished_games = data.get_unfinished_games()
    for game in unfinished_games:
        game_id = game["id"]
        collect_ratings(game_id, page_counter=game["page"])

        print("now remove duplicates")

        game_name = bgg.find_game_name(game_id)
        filepath = data.create_rating_items_path(game_id, game_name)
        data.remove_duplicates_from_csv(filepath)

    return


def main():

    parser = argparse.ArgumentParser()

    # -db DATABSE -u USERNAME -p PASSWORD -size 20
    parser.add_argument(
        "-f",
        "--finish",
        dest="finish",
        help="Set if you want to complete unfinished games",
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()

    if args.finish is True:
        finish_games()
        return

    ids_to_be_collected: list[str] = []
    list_of_top_games: list[dict] = []
    with open("top_games/bgg_top_1000.json", encoding="utf-8") as json_file:
        list_of_top_games = json.load(json_file)
        for game in list_of_top_games:
            ids_to_be_collected.append(game["id"])

    collected_games = os.listdir(data.CSV_FOLDER)

    for game_id in ids_to_be_collected:

        # Check if we already have a csv file starting with the id
        if any(game_id == csv_file.split("_")[0] for csv_file in collected_games):
            print(f"Already have game with id {game_id}")
            continue
        print(f"Will now collect game with id {game_id}")

        # game_information = next(
        #     game for game in list_of_top_games if game["id"] == game_id
        # )

        collect_ratings(game_id)

        # further = input("Continue? Just hit Enter")
        # if further != "":
        #     break


if __name__ == "__main__":
    main()
