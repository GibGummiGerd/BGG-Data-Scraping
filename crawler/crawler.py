"crawler.py"

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, Comment, NavigableString, Tag


URL_LINK = "https://boardgamegeek.com/boardgame/167355/nemesis/ratings?pageid=2"


def start_driver() -> BeautifulSoup:
    """_summary_

    Returns:
        BeautifulSoup: _description_
    """
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    # driver.minimize_window()
    driver.get(URL_LINK)

    page = driver.page_source

    driver.close()
    return page


def get_information(soup: BeautifulSoup):
    """_summary_

    Args:
        soup (BeautifulSoup): _description_
    """
    text = extract_rating_information(soup)
    with open("text.txt", "w", encoding="utf-8") as f:
        f.write(str(text))
        # for i in text:
        #     f.write(i.string.strip() + "\n")


def extract_rating_information(soup: BeautifulSoup) -> list[dict]:
    """_summary_

    Args:
        soup (BeautifulSoup): _description_

    Returns:
        _type_: _description_
    """
    all_ratings_tag = soup.find(
        "ul",
        attrs={
            "class": "summary summary-callout summary-callout-lg summary-rating summary-relaxed"
        },
    )
    list_of_all_rating_tags = all_ratings_tag.find_all(
        "li", attrs={"class": "summary-item summary-rating-item ng-scope"}
    )

    list_of_rating_dicts = list()

    print(len(list_of_all_rating_tags))
    for single_rating_tag in list_of_all_rating_tags:
        single_rating_tag: Tag

        rating_number_tag = single_rating_tag.find(
            "div", attrs={"class": "rating-angular"}
        )

        # find rating given, if no number given it was deleted and rating of user will be ignored
        rating_number = rating_number_tag.string.strip()
        if rating_number == "":
            continue

        info_tag = single_rating_tag.find("div", attrs={"class": "comment-header-info"})

        # username
        username = info_tag.a.string

        # timestamp
        timestamp_tag = info_tag.find(
            "span", attrs={"class": "comment-header-timestamp"}
        )
        timestamp_cleaned = (
            timestamp_tag.span["title"].replace("Last updated:", "").rstrip().lstrip()
        )

        # country
        country_tag = info_tag.find("div", attrs={"class": "comment-header-location"})
        inner_country = country_tag.find(
            "span",
            attrs={
                "ng-if": "::item.user.country != ''",
                "class": "ng-binding ng-scope",
            },
        )
        country = ""
        if inner_country is not None:
            comments = inner_country.find_all(
                string=lambda text: isinstance(text, NavigableString)
            )
            country = comments[-1].replace("\t", "").rstrip().lstrip()

        # collection
        collection = ""

        collection_tag = single_rating_tag.find(
            "span",
            attrs={
                "ng-repeat-start": "status in ::ratingsctrl.config.allstatuses",
                "ng-if-start": "::item.status[status.key]",
                "class": "ng-binding ng-scope",
            },
        )

        if collection_tag is not None:
            read_collection = collection_tag.string.rstrip().lstrip()
            if read_collection == "Own" or "Prev. Owned":
                collection = read_collection

        # comment
        comment = ""
        comment_tag = single_rating_tag.find(
            "span",
            attrs={
                "ng-bind-html": "::item.textfield.comment.rendered|to_trusted",
                "class": "ng-binding ng-scope",
            },
        )
        if comment_tag is not None:
            comment = comment_tag.string

        rating_dict = {
            "rating": rating_number,
            "user": username,
            "timestamp": timestamp_cleaned,
            "country": country,
            "collection": collection,
            "comment": comment,
        }

        print("------------------------------------")
        print(rating_dict)

        list_of_rating_dicts.append(rating_dict)

    return list_of_rating_dicts


def main():
    """_summary_"""
    first_soup = BeautifulSoup(start_driver(), "lxml")

    with open("2.txt", "w", encoding="utf-8") as f:
        f.write(first_soup.prettify())

    get_information(first_soup)

    print("----------------------------------------------")
    print("--------------  Successful Run  --------------")
    print("----------------------------------------------")


if __name__ == "__main__":
    main()
