"""bgg.py"""

from datetime import datetime
from pathlib import Path
import time
import os
import json
import requests
import pandas
from bs4 import BeautifulSoup


def call_stuff(game_id: str, page_id: int) -> dict:

    url = f"https://api.geekdo.com/api/collections?objectid={game_id}&objecttype=thing&oneperuser=1&pageid={page_id}&require_review=true&showcount=50&sort=review_tstamp"
    get_response = requests.get(url)
    received_json_bytes = json.loads(get_response.content)

    return received_json_bytes


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

    return info["name"]


def create_data_structure(user_item_bytes: bytes) -> list:

    user_items = list()

    for user_item in user_item_bytes["items"]:

        comment = user_item["textfield"]["comment"]["value"]
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


def flow(game_id: str):

    game_name = get_game_name(game_id).replace(" ", "_")

    i = 1
    output_path = os.path.join("csv", f"{game_id}_{game_name}_rating_items.csv")
    Path("csv").mkdir(parents=True, exist_ok=True)

    if os.path.exists(output_path):
        print(
            "File for game already exists. \nStopping processing to not overwrite content"
        )
        return

    found_items = True
    start_time = datetime.now()

    while found_items:

        time.sleep(4)

        json_bytes = call_stuff(game_id, i)

        user_dict_list = create_data_structure(json_bytes)

        pandas.DataFrame(user_dict_list).to_csv(
            output_path, mode="a", header=not os.path.exists(output_path), index=False
        )

        print(
            ". . . . . . . . . . .\n"
            + "Current run time: "
            + str(datetime.now() - start_time)
            + "\nRatings: "
            + str((i - 1) * 50)
            + " to "
            + str(i * 50)
        )

        if len(user_dict_list) == 0:
            found_items = False
            print("Reached last ratings")
            print("-----------------------------------")

        i = i + 1


def main():

    game_id = "167355"

    flow(game_id)


if __name__ == "__main__":
    main()
