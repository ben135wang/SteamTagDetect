import requests
import json


num_pages = 10
req_replies = {}
for page_num in range(num_pages):
    r = requests.get("http://steamspy.com/api.php?", params={"request": "all", "page": page_num})
    req_replies.update(r.json())

with open('top_games.json', 'w') as outfile:
    json.dump(req_replies, outfile)

print(len(req_replies))