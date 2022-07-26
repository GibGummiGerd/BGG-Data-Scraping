"""bgg.py"""

from datetime import datetime
import time
import os
import json
import requests
import pandas


def call_stuff(game_id: str, page_id: int) -> dict:
    # page_id = "200"
    url = f"https://api.geekdo.com/api/collections?objectid={game_id}&objecttype=thing&oneperuser=1&pageid={page_id}&require_review=true&showcount=50&sort=review_tstamp"
    get_response = requests.get(url)
    received_json_bytes = json.loads(get_response.content)
    print(received_json_bytes)
    return received_json_bytes


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


def flow():
    game_id = "292974"

    i = 1
    output_path = "tournament_at_avalon_rating_items.csv"
    found_items = True
    start_time = datetime.now()

    while found_items:

        time.sleep(5)

        json_bytes = call_stuff(game_id, i)

        user_dict_list = create_data_structure(json_bytes)

        pandas.DataFrame(user_dict_list).to_csv(
            output_path, mode="a", header=not os.path.exists(output_path), index=False
        )

        if len(user_dict_list) == 0:
            found_items = False
            print("xDDDDDDD")

        i = i + 1

        print("Aktuelle Zeit: " + str(datetime.now() - start_time) + "\n ")

    # print(cont)

    # pandas.DataFrame(user_dict_list).to_csv(
    #     "out.csv", mode="a", header=False, index=False
    # )


def main():
    flow()


if __name__ == "__main__":
    main()
