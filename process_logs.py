import csv
import json
import re


class REMatcher(object):
    def __init__(self, matchstring):
        self.matchstring = matchstring

    def match(self, regexp):
        self.rematch = re.match(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self, i):
        return self.rematch.group(i)


events = {}

regex = "Unable to process event, no start date for event: (.*)"

with open('downloaded-logs-20220930-094631.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        m = REMatcher(row[4])
        if m.match(regex):
            id = m.group(1)
            events[id] = id

print(events)

open('no_start_dates.json', 'w').write(
    json.dumps(list(events.keys()), indent=2))
