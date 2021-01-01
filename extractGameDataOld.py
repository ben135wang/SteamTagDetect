import json
import re
import requests
from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen

steam_store_url = "https://store.steampowered.com/app/"
screenshot_class = "highlight_player_item highlight_screenshot"
movie_class = "highlight_player_item highlight_movie"
description_class = "game_area_description"
sc_folder = ".\\media\\sc\\"
mov_folder = ".\\media\\mov\\"

with open('top_games.json') as json_file:
    games = json.load(json_file)

start_index = 0
for index in range(start_index, len(games.keys())):

    game = games[list(games)[index]]
    name = game["name"]
    clean_name = re.sub(r'[/\\*:?\"<>|]', '', name)
    app_id = str(game["appid"])
    print(str(index) + " Game: " + name)

    # Game details from steamspy
    try:
        game_details = requests.get("https://steamspy.com/api.php?", params={"request": "appdetails", "appid": app_id})
        print(game_details)
        game_details = game_details.json()
    except json.decoder.JSONDecodeError:
        print("    couldn't find game")
        continue

    # Scrape steam store page
    try:
        client = urlopen(steam_store_url + app_id)
        game_html = client.read()
        client.close()
    except urllib.error.HTTPError:
        print("    page not found")
        continue

    game_soup = BeautifulSoup(game_html, "html.parser")

    # Get screenshots
    screenshot_containers = game_soup.find_all("div", {"class": screenshot_class})
    screenshot_paths = []
    for sc_index in range(len(screenshot_containers)):
        r = requests.get(screenshot_containers[sc_index].div.a["href"])
        path = sc_folder + name + "-" + str(sc_index) + ".jpg"
        screenshot_paths.append(path)
        with open(path, "wb") as pic:
            pic.write(r.content)
    game_details["screenshots"] = screenshot_paths

    # Get Movies
    movie_containers = game_soup.find_all("div", {"class": movie_class})
    movie_paths = []
    for mv_index in range(len(movie_containers)):
        r = requests.get(movie_containers[mv_index]["data-mp4-source"])
        path = mov_folder + name + "-" + str(mv_index) + ".mp4"
        movie_paths.append(path)
        with open(path, "wb") as mov:
            mov.write(r.content)
    game_details["movies"] = movie_paths

    # Get game description
    description_container = game_soup.find("div", {"id": description_class})
    clean_description = re.sub(r'About\sThis\sGame', '', description_container.text).strip()
    game_details["description"] = clean_description