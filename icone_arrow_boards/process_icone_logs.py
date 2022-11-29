import json

# (2022[0-9]{4}-[0-9]{6})

segments = []
start_time = None
end_time = None
prevID = None
dir = '2022_11_08'
file_name = 'icone_log_20221108-094339'
with open(f'./{dir}/{file_name}.txt', 'r') as f:
    for line in f.readlines():
        items = line.strip('\n').split('; ')
        ts = items[0]
        if not start_time:
            start_time = ts
        end_time = ts
        print(ts)
        if len(items) == 1:
            if prevID:
                segments[-1]['end_time'] = ts
            prevID = None
            print("NENENENE")
            continue
        info = items[1].split(', ')
        currentID = info[0].split(': ')[-1].split('_')[0][1:]
        state = info[2].split(': ')[-1][2:-1]
        coordinates = info[4].split(': ')[-1].split(',')

        if prevID:
            print("APPENDING")
            segments[-1]['end_time'] = ts
            segments[-1]['coordinates'].append(
                [float(coordinates[1]), float(coordinates[0])])
            if state not in segments[-1]['states']:
                segments[-1]['states'].append(state)

        if currentID != prevID:
            print(currentID, prevID)
            print("CREATING")
            segments.append({'start_time': ts, 'end_time': ts,
                            'id': currentID, 'states': [state],
                             'coordinates': [[float(coordinates[1]), float(coordinates[0])]]})

        prevID = currentID

results = {'start_time': start_time, 'end_time': end_time, 'results': segments}
print(json.dumps(results, indent=2))
print(f'./{dir}/{file_name}.json')
with open(f'./{dir}/{file_name}.json', 'w') as f:
    f.write(json.dumps(results, indent=2))
