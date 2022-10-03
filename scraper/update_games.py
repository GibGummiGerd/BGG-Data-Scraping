from datetime import datetime
from sqlite3 import Timestamp
import pandas
import time
import sys
import os
import numpy

from bgg import *
from data import *
from files import *
from const import *
from operations import *


def get_new_ratings(game_id, page_id, max_fails=MAX_FAILS, sleep_time=SLEEP_TIME):

    fail_counter = 0
    while fail_counter <= max_fails:

        json_bytes, ok = rating_request(game_id, page_id)
        if not ok:
            fail_counter = fail_counter + 1
            time.sleep(sleep_time)
            continue

        return create_list_of_rating_items(json_bytes)

    print(f"Failed {max_fails} times in  a row to get a request. Ending process.")
    sys.exit()


def update_ratings(game_id, csv_file):

    # get existing csv file
    data_frame = open_csv_by_name(csv_file)

    # latest date in existing csv file
    last_date = numpy.nan
    counter = 0
    while pandas.isna(last_date):
        last_date = later_date(
            str_to_time(data_frame.iloc[counter][RATING_DATETIME]),
            str_to_time(data_frame.iloc[counter][COMMENT_DATETIME]),
        )
        counter = counter + 1

    page_counter = 1

    while True:
        retrieved_ratings = []
        retrieved_ratings = retrieved_ratings + get_new_ratings(game_id, page_counter)

        last_date_of_retrieved_ratings = None
        counter = 1
        while pandas.isna(last_date_of_retrieved_ratings):
            last_date_of_retrieved_ratings = later_date(
                str_to_time(retrieved_ratings[RATING_COUNT - counter][RATING_DATETIME]),
                str_to_time(
                    retrieved_ratings[RATING_COUNT - counter][COMMENT_DATETIME]
                ),
            )
            counter = counter + 1

        # Ältester schon vorhandener Eintrag ist älter als neuer

        retrieved_ratings = pandas.DataFrame.from_dict(retrieved_ratings)
        data_frame = pandas.concat([retrieved_ratings, data_frame], ignore_index=True)

        print(f"Date reached: {last_date_of_retrieved_ratings}")
        print(f"Date in csv: {last_date}")

        if last_date >= last_date_of_retrieved_ratings:

            data_frame.replace(
                {
                    RATING_DATETIME: "0000-00-00 00:00:00",
                    COMMENT_DATETIME: "0000-00-00 00:00:00",
                },
                numpy.nan,
                inplace=True,
            )

            data_frame[LATEST_TSTAMP] = data_frame.apply(
                create_latest_tstamp_column,
                axis=1,
            )

            data_frame = data_frame[data_frame[LATEST_TSTAMP].notnull()]

            data_frame.sort_values(by=LATEST_TSTAMP, inplace=True, ascending=False)

            data_frame.reset_index(drop=True, inplace=True)

            data_frame.drop_duplicates(subset=[USERNAME], inplace=True, keep="first")

            game_info = find_game_info(game_id)
            output_filename = create_csv_file_name_with_date(game_id, game_info["name"])
            output_filepath = os.path.join(CSV_FOLDER, output_filename)

            save_rating_item_dict(data_frame, output_filepath, write_mode="w")

            return output_filename

        page_counter = page_counter + 1

        time.sleep(SLEEP_TIME)

    return


def update_games(games_to_be_updated):

    # read existing csv file X
    # Load 50 ratings X
    # save ratings in list
    # Check how many of entries are already in list
    # if over treshold stop loading
    # remove duplicates
    # save new items

    print(games_to_be_updated)

    found_csv = find_csv_by_id(games_to_be_updated)

    for game_id, csv_file in found_csv.items():

        print(f"working on ID {game_id}, remaining {len(games_to_be_updated)}")

        updated_file = update_ratings(game_id, csv_file)
        games_to_be_updated.remove(game_id)

        if updated_file != csv_file:
            os.remove(create_csv_folder_path_from_filename(csv_file))

        print(f"finished ID {game_id}")

        with open("finished.txt", "a") as f:
            f.write(f"{game_id}\n")

    return
