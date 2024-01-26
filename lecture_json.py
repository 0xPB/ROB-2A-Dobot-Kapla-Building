import json

with open('construction.json', "rb") as json_data:
    kapla_list = json.load(json_data)
    donnees = sorted(kapla_list, key=lambda b: (b["base"][2], b["base"][1], b["base"][0]))
    print(*donnees, sep="\n")

