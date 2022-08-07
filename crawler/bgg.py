"""bgg.py"""

import json

from bs4 import BeautifulSoup
from operations import get_request


def rating_request(game_id: str, page_id: int) -> tuple[dict, bool]:
    """Makes a call to the bgg api. Returns retrieved data

    Args:
        game_id (str): ID of the game
        page_id (int): number of rating page

    Returns:
        dict: Returned json object from api call transformed into a python dict
        bool: Returns False if the json contains an "errors" field
    """

    url = f"https://api.geekdo.com/api/collections?objectid={game_id}&objecttype=thing&oneperuser=1&pageid={page_id}&require_review=true&showcount=50&sort=review_tstamp"
    get_response = get_request(url)

    received_json_bytes = json.loads(get_response.content)

    # Check for errors in the return
    if "errors" in received_json_bytes:
        print(received_json_bytes["errors"])
        return received_json_bytes, False

    return received_json_bytes, True


def find_game_name(game_id: str) -> str:
    """get name of game belonging to game ID

    Args:
        game_id (int): _description_

    Returns:
        str: _description_
    """
    url = f"https://boardgamegeek.com/boardgame/{game_id}"
    get_response = get_request(url)

    soup = BeautifulSoup(get_response.text, "html.parser")
    ld_json_tag = soup.find("script", attrs={"type": "application/ld+json"})
    info: dict = json.loads(ld_json_tag.string)

    game_name_cleaned = info["name"].lstrip().rstrip()

    return game_name_cleaned


def find_game_info(game_id: str) -> dict:

    url = f"https://boardgamegeek.com/boardgame/{game_id}"
    get_response = get_request(url)

    soup = BeautifulSoup(get_response.text, "html.parser")
    ld_json_tag = soup.find("script", attrs={"type": "application/ld+json"})
    all_info: dict = json.loads(ld_json_tag.string)

    game_info = {
        "id": game_id,
        "voters": int(all_info["aggregateRating"]["reviewCount"]),
        "name": all_info["name"].lstrip().rstrip(),
    }

    return game_info
