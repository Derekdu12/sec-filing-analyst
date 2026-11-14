# Helper: list the labels a company uses that contain a certain word,
# and the most recent year each label has data for.
#
# Change TICKER and WORD below, then press F5.

import json

TICKER = "CVS"
WORD = "PerShare"

file = open("data/" + TICKER + "/companyfacts.json")
facts = json.load(file)
file.close()

for label in facts["facts"]["us-gaap"]:
    if WORD.lower() in label.lower():
        units = facts["facts"]["us-gaap"][label]["units"]
        unit_name = list(units.keys())[0]
        newest = ""
        for entry in units[unit_name]:
            if entry["end"] > newest:
                newest = entry["end"]
        print(newest, label)
