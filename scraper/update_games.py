from datetime import datetime
from sqlite3 import Timestamp
import pandas
import time
import sys
import os
import numpy

from bgg import rating_request
import data
import files
from const import *
from operations import later_date, str_to_time


def get_new_ratings(game_id, page_id, max_fails=MAX_FAILS, sleep_time=SLEEP_TIME):

    fail_counter = 0
    while fail_counter <= max_fails:

        json_bytes, ok = rating_request(game_id, page_id)
        if not ok:
            fail_counter = fail_counter + 1
            time.sleep(sleep_time)
            continue

        return data.create_list_of_rating_items(json_bytes)

    print(f"Failed {max_fails} times in  a row to get a request. Ending process.")
    sys.exit()


def update_ratings(game_id, csv_file):

    # get existing csv file
    data_frame = files.open_csv_by_name(csv_file)

    print(data_frame.iloc[6][COMMENT_DATETIME])

    # latest date in existing csv file
    last_date = ""
    counter = 0
    while last_date == "":
        last_date = later_date(
            str_to_time(data_frame.iloc[counter][RATING_DATETIME]),
            str_to_time(data_frame.iloc[counter][COMMENT_DATETIME]),
        )
        counter = counter + 1

    retrieved_ratings = []
    page_counter = 1

    while True:
        retrieved_ratings = retrieved_ratings + get_new_ratings(game_id, page_counter)

        print((retrieved_ratings[49][RATING_DATETIME]))
        print((retrieved_ratings[49][COMMENT_DATETIME]))

        last_date_of_current_ratings = None
        counter = 1
        while last_date_of_current_ratings == None:
            last_date_of_current_ratings = later_date(
                str_to_time(retrieved_ratings[RATING_COUNT - counter][RATING_DATETIME]),
                str_to_time(
                    retrieved_ratings[RATING_COUNT - counter][COMMENT_DATETIME]
                ),
            )
            counter = counter + 1

        print("current " + str(last_date_of_current_ratings))
        print("update " + str(last_date))

        # Ältester schon vorhandener Eintrag ist älter als neuer
        if last_date >= last_date_of_current_ratings:
            retrieved_ratings = pandas.DataFrame.from_dict(retrieved_ratings)
            data_frame = pandas.concat(
                [retrieved_ratings, data_frame], ignore_index=True
            )

            data_frame.replace(
                {
                    RATING_DATETIME: "0000-00-00 00:00:00",
                    COMMENT_DATETIME: "0000-00-00 00:00:00",
                },
                numpy.nan,
                inplace=True,
            )

            data_frame[LATEST_DATETIME] = data_frame.apply(
                data.create_latest_tstamp_column,
                axis=1,
            )

            data_frame = data_frame[data_frame[LATEST_DATETIME].notnull()]

            data_frame.reset_index(drop=True, inplace=True)

            data_frame.sort_values(by=LATEST_DATETIME, inplace=True, ascending=False)

            duppies = data_frame.duplicated(subset=[USERNAME], keep=False)
            for index, value in duppies.items():
                if value:
                    print(index)
                    print(data_frame.iloc[index][USERNAME])

            data_frame.drop_duplicates(subset=[USERNAME], inplace=True, keep="first")

            data.save_rating_item(data_frame, csv_file, write_mode="w")
            return

        page_counter = page_counter + 1
        break
    return


def update_games(games_to_be_updated):

    # read existing csv file X
    # Load 50 ratings X
    # save ratings in list
    # Check how many of entries are already in list
    # if over treshold stop loading
    # remove duplicates
    # save new items

    found_csv = files.find_csv_by_id(games_to_be_updated)

    for game_id, csv_file in found_csv.items():
        update_ratings(game_id, csv_file)
        games_to_be_updated.remove(game_id)

    print(found_csv)
    print(games_to_be_updated)
    return
