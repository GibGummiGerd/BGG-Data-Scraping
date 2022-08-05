"""bgg.py"""

from datetime import datetime
from pathlib import Path
import time
import os
import json
import pandas


from bgg import rating_request, find_game_name
from operations import slugify
from data import create_list_of_rating_items


def get_ratings_for_game(game_id: str, game_information: dict):

    sleep_time = 3.8

    game_name = find_game_name(game_id)
    cleaned_game_name = slugify(game_name)

    estimated_ratings = game_information["number_voters"] * 1.03

    output_path = os.path.join("csv", f"{game_id}_{cleaned_game_name}_rating_items.csv")
    Path("csv").mkdir(parents=True, exist_ok=True)

    if os.path.exists(output_path):
        print(
            "File for game already exists. \nStopping processing to not overwrite content"
        )
        return

    found_items = True
    start_time = datetime.now()

    page_counter = 1
    fail_counter = 1
    while found_items and fail_counter < 10:

        time.sleep(sleep_time)

        json_bytes, ok = rating_request(game_id, page_counter)
        if not ok:
            sleep_time = sleep_time + 0.1
            fail_counter = fail_counter + 1
            # wait to not directly run into request limit again
            time.sleep(5)
            continue

        user_dict_list = create_list_of_rating_items(json_bytes)

        estimated_time = (estimated_ratings / 50 - page_counter) * sleep_time
        estimated_min = int(estimated_time // 60)
        estimated_sec = int((estimated_time / 60) % 1 * 60)

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

        if len(user_dict_list) == 0:

            found_items = False
            print("Reached last ratings")
            print("-----------------------------------")
            break

        pandas.DataFrame(user_dict_list).to_csv(
            output_path, mode="a", header=not os.path.exists(output_path), index=False
        )

        with open(f"csv/tmp_{game_id}.txt", "w", encoding="utf-8") as temp_file:
            temp_file.write(
                f"id: {game_id}\npage: {page_counter}\nrating: {page_counter * 50}"
            )

        page_counter = page_counter + 1
        fail_counter = 0

    if fail_counter > 10:
        with open(output_path, "a", encoding="utf-8") as csv_file:
            csv_file.write("Did not get all the data\n")
        return

    with open("csv/finished.txt", "a", encoding="utf-8") as finished_file:
        finished_file.write(f"{game_id}\n")

    os.remove(f"csv/tmp_{game_id}.txt")

    return


def main():

    ids_to_be_collected = []
    list_of_top_games: list[dict] = []
    with open("top_games/bgg_top_1000.json", encoding="utf-8") as json_file:
        list_of_top_games = json.load(json_file)
        for game in list_of_top_games:
            ids_to_be_collected.append(game["id"])

    collected_games = os.listdir("csv")

    for game_id in ids_to_be_collected:
        if any(game_id in csv_file for csv_file in collected_games):
            print(f"Already have game with id {game_id}")
            continue
        print(f"Will now collect game with id {game_id}")

        game_information = next(
            game for game in list_of_top_games if game["id"] == game_id
        )
        get_ratings_for_game(game_id, game_information)

        # further = input("Continue? Just hit Enter")
        # if further != "":
        #     break


if __name__ == "__main__":
    main()
