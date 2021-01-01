import json
import jsonlines
import re
import requests
import time
from bs4 import BeautifulSoup

steam_store_api = "https://store.steampowered.com/api/appdetails?"

#When true, also download related screenshots and promotional videos
download = False
sc_folder = ".\\media\\sc\\"
mov_folder = ".\\media\\mov\\"

with open('top_games.json') as json_file:
    games = json.load(json_file)

# Example game from top_games.json:
    # "570": {appid=570, name="Dota 2", developer="Valve", publisher="Valve", score_rank="", positive=1206694,
    #             negative=221642, userscore=0, owners="100,000,000 .. 200,000,000", average_forever=36567,
    #             average_2weeks=1517, median_forever=1236, median_2weeks=741, price="0", initialprice="0",
    #             discount="0", ccu=618777}


start_index = 5041
with jsonlines.open("detailed_games.jsonl", "a") as detailed_games:
    # Iterate through all top games
    for index in range(start_index, len(games.keys())):

        game = games[list(games)[index]]
        name = game["name"]
        clean_name = re.sub(r'[/\\*:?\"<>|]', '', name)  # Clean name for use in file storage
        app_id = str(game["appid"])
        print(str(index) + " Game: " + name)

        success = False
        timeout_count = 0
        while not success:
            try:
                steam_details = requests.get(steam_store_api, params={"appids": app_id, "language": "english"})
                steam_details = steam_details.json()
                steam_details = steam_details[app_id]
                success = True
            except json.decoder.JSONDecodeError:
                print("    steam api call failed: " + str(steam_details))
                break
            except TypeError:
                timeout_count += 1
                print("    steam api call timeout: " + str(timeout_count))
                time.sleep(max(250 / timeout_count, 10))

        if not success or not steam_details["success"]:
            print("    couldn't find game")
            continue

        detailed_game = game.copy()
        detailed_game.update(steam_details["data"])

        if download:
            if "screenshots" in detailed_game:
                screenshots = detailed_game["screenshots"]
                screenshot_paths = []
                count = 1
                for sc_dict in screenshots:
                    r = requests.get(sc_dict["path_full"])
                    path = sc_folder + clean_name + "-" + str(count) + ".jpg"
                    count += 1
                    screenshot_paths.append(path)
                    with open(path, "wb") as pic:
                        pic.write(r.content)

                detailed_game["screenshots"] = screenshot_paths

            if "movies" in detailed_game:
                movies = detailed_game["movies"]
                movie_paths = []
                count = 1
                for mv_dict in movies:
                    r = requests.get(mv_dict["mp4"]["480"])
                    path = mov_folder + clean_name + "-" + str(count) + ".mp4"
                    count += 1
                    movie_paths.append(path)
                    with open(path, "wb") as mov:
                        mov.write(r.content)

                detailed_game["movies"] = movie_paths

        if "detailed_description" in detailed_game:
            description = detailed_game["detailed_description"].strip()
            soup = BeautifulSoup(description, 'html.parser')
            detailed_game["detailed_description"] = soup.get_text()

        if "about_the_game" in detailed_game:
            about = detailed_game["about_the_game"].strip()
            soup = BeautifulSoup(about, 'html.parser')
            detailed_game["about_the_game"] = soup.get_text()

        if "short_description" in detailed_game:
            desc = detailed_game["short_description"].strip()
            soup = BeautifulSoup(desc, 'html.parser')
            detailed_game["short_description"] = soup.get_text()

        detailed_games.write(detailed_game)
