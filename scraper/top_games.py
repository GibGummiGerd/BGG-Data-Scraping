from pathlib import Path
import argparse, sys
import math
import json
import requests
from datetime import date
import time
from bs4 import BeautifulSoup


def create_json_of_top_games(
    to_rank: int = 100, directory_path: str = "top_games", use_no_date: bool = False
):
    """_summary_

    Args:
        to_rank (int, optional): Rank until which games are collected. Defaults to 100.
        directory_path (str, optional): Relative directory path where file should be saved. Defaults to "top_games".
        use_date (bool, optional): If date should be saved in file name. Defaults to True.

    Returns:
        _type_: Return nothing.
    """

    page_id = 0
    overall_rank = 0
    list_of_ranks = []
    reached_rank = False

    while page_id <= math.ceil(to_rank / 100):

        page_id += 1

        url = f"https://boardgamegeek.com/browse/boardgame/page/{page_id}"
        get_return = requests.get(url)
        soup = BeautifulSoup(get_return.content, "lxml")
        all_id_elements = soup.find_all("a", attrs={"class": "primary"})
        all_rating_elements = soup.find_all(
            "td", attrs={"class": "collection_bggrating"}
        )

        rank_in_list = 0
        for element in all_id_elements:

            overall_rank += 1
            rank_in_list += 1

            # get id and name
            id_and_name_element: str = element["href"]
            id_and_name = id_and_name_element.split("/boardgame/", 1)[1]
            game_id = id_and_name.split("/", 1)[0]
            game_name = id_and_name.split("/", 1)[1]

            # get ratings and voters
            geek_rating: str
            geek_rating = all_rating_elements[rank_in_list * 3 - 3].string
            geek_rating = geek_rating.strip()
            geek_rating = f"{float(geek_rating):.3f}"
            average_rating: str
            average_rating = all_rating_elements[rank_in_list * 3 - 2].string
            average_rating = average_rating.strip()
            average_rating = f"{float(average_rating):.2f}"
            number_voters: str
            number_voters = all_rating_elements[rank_in_list * 3 - 1].string
            number_voters = number_voters.strip()
            number_voters = int(number_voters)

            game = {
                "rank": overall_rank,
                "id": game_id,
                "name": game_name,
                "geek_rating": geek_rating,
                "average_rating": average_rating,
                "number_voters": number_voters,
            }
            list_of_ranks.append(game)

            if overall_rank >= to_rank:
                reached_rank = True
                break

        print(f"Site: {page_id}, found {overall_rank} games")

        if reached_rank is True:
            break

        time.sleep(4)

    output = ""
    if use_no_date is True:
        output = f"{directory_path}/bgg_top_{to_rank}.json"
    else:
        today = str(date.today())
        output = f"{directory_path}/bgg_top_{to_rank}_{today}.json"
    Path(f"{directory_path}").mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as json_file:
        json.dump(list_of_ranks, json_file)

    print(f"Successfully found the top {to_rank} games.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get top rated games from BoardGameGeek(BGG)"
    )

    parser.add_argument(
        "-r",
        "--rank",
        dest="rank",
        help="Rank until which you want to get the top list",
        type=int,
        default=100,
        required=False,
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="path",
        help="Path to directory where file should be saved",
        type=str,
        default="top_games",
        required=False,
    )
    parser.add_argument(
        "-nd",
        "--nodate",
        dest="no_date",
        help="False, if date should not be added to file name",
        type=bool,
        default=False,
        required=False,
        action=argparse.BooleanOptionalAction,
    )

    args = parser.parse_args()
    create_json_of_top_games(
        to_rank=args.rank, directory_path=args.path, use_no_date=args.no_date
    )
