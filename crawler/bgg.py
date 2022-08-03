"""bgg.py"""

from datetime import datetime
from pathlib import Path
import time
import os
import json
import requests
import pandas
from bs4 import BeautifulSoup

from operations import slugify


def make_bgg_api_call(game_id: str, page_id: int) -> tuple[dict, bool]:
    """Makes a call to the bgg api. Returns retrieved data

    Args:
        game_id (str): ID of the game
        page_id (int): number of rating page

    Returns:
        dict: Returned json object from api call transformed into a python dict
        bool: Returns False if the json contains an "errors" field
    """

    url = f"https://api.geekdo.com/api/collections?objectid={game_id}&objecttype=thing&oneperuser=1&pageid={page_id}&require_review=true&showcount=50&sort=review_tstamp"

    get_response = requests.get(url)

    received_json_bytes = json.loads(get_response.content)

    # Check for errors in the return
    if "errors" in received_json_bytes:
        print(received_json_bytes["errors"])
        return received_json_bytes, False

    return received_json_bytes, True


def get_list_of_ids() -> list[int]:
    list_of_games: list[dict] = []
    list_of_ids: list[int] = []
    with open("bgg_top_1000_2022-07-31.json", encoding="utf-8") as json_file:
        list_of_games = json.load(json_file)
    for game in list_of_games:
        list_of_ids.append(game["id"])
    return list_of_ids


def get_game_name(game_id: str) -> str:
    """get name of game belonging to game ID

    Args:
        game_id (int): _description_

    Returns:
        str: _description_
    """
    url = f"https://boardgamegeek.com/boardgame/{game_id}"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    ld_json_tag = soup.find("script", attrs={"type": "application/ld+json"})
    info = json.loads(ld_json_tag.string)

    # clean name of illegal characters
    cleaned_name = slugify(info["name"])

    return cleaned_name


def create_data_structure(user_item_bytes: bytes) -> list:

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


def get_ratings_for_game(game_id: str):

    sleep_time = 3.8

    game_name = get_game_name(game_id)

    output_path = os.path.join("csv", f"{game_id}_{game_name}_rating_items.csv")
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

        json_bytes, ok = make_bgg_api_call(game_id, page_counter)
        if not ok:
            sleep_time = sleep_time + 0.1
            fail_counter = fail_counter + 1
            # wait to not directly run into request limit again
            time.sleep(5)
            continue

        user_dict_list = create_data_structure(json_bytes)

        print(
            ". . . . . . . . . . .\n"
            + f"Game: {game_name} (ID: {game_id}) \nCurrent run time: "
            + str(datetime.now() - start_time)
            + f"\nPage: {page_counter}\nRatings: "
            + str((page_counter - 1) * 50)
            + " to "
            + str(page_counter * 50)
            + f"; one request every {sleep_time} seconds"
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
        get_ratings_for_game(game_id)

        # further = input("Continue? Just hit Enter")
        # if further != "":
        #     break


if __name__ == "__main__":
    main()
