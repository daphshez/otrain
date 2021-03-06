from csv import DictReader, DictWriter
import csv
from zipfile import ZipFile
from io import TextIOWrapper
from collections import Counter


def match():
    gtfs_file_name = 'data/gtfs/merged/stops_20150401_20150630.txt'

    otrain_fields = "Train_Date,Train_Number,Planned,Station_number,Station_Description,Station_Order,Route_Description,Station_typ,Planned_Stop,Actual_Stop,Planned_Depratur,Actual_Departure,Planned_Arrival,Actual_Arrival".split(',')
    extra_fields = "arrival_time,departure_time,stop_sequence,gtfs_date".split(',')

    print("Loading gtfs data from", gtfs_file_name)
    gtfs_lines = [line for line in open(gtfs_file_name)]

    def make_gtfs_key(r):
        (train_date, _, train_number) = r['trip_id'].partition('_')
        return train_date, int(train_number), r['stop_id']

    # gtfs_data is a mapping from the key (date, route_id, stop_id, arrival_time) to a pair of the line and the line
    # number. Line number helps to easily find out later which gtfs lines were succesfully matched.
    gtfs_data = {make_gtfs_key(r): (r, i) for (i, r) in enumerate(DictReader(gtfs_lines))}

    matched_gtfs_lines = set()

    def make_otrain_key(r):
        def reformat_date(d):
            return d[:2] + d[3:5] + d[8:]

        return reformat_date(r['Train_Date']), int(r['Train_Number']), r['Station_number']

    def match(r):
        gtfs_record = gtfs_data.get(make_otrain_key(r), None)
        if gtfs_record:
            matched_gtfs_lines.add(gtfs_record[1])
            return gtfs_record[0]

    def enrich(r, gtfs_record):
        if gtfs_record:
            for key in extra_fields:
                r[key] = gtfs_record[key]
        return {key: r.get(key, '') for key in otrain_fields + extra_fields}

    print("Matching records and writing updated otrain data")
    with open(r'data/otrain_gtfs/otrain_2015_04_05_06.csv', 'w', encoding='utf8', newline='') as o:
        writer = DictWriter(o, fieldnames=otrain_fields + extra_fields)
        writer.writeheader()
        with ZipFile(r'data\otrain\2015_04_05_06.zip') as z:
            with z.open('2015_04_05_06.txt') as f:
                reader = DictReader(TextIOWrapper(f, 'utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)
                for r in reader:
                    writer.writerow(enrich(r, match(r)))

    # write a copy of the gtfs file with an extra field to whether to record was used
    print("Writing updated gtfs")
    with open(r'data/otrain_gtfs/gtfs_2015_04_05_06.csv', 'w', encoding='utf8') as f:
        f.write(gtfs_lines[0].strip() + ',matched\n')
        for i, line in enumerate(gtfs_lines[1:]):
            line = line.strip() + "," + str(i in matched_gtfs_lines) + "\n"
            f.write(line)

    # print some stats :-)
    print('matched:', len(matched_gtfs_lines), len(matched_gtfs_lines) / len(gtfs_data), 'of gtfs records')


def compare_times():
    def fp(f):
        return "{0:.4f}%".format(f * 100)

    with open(r'data/otrain_gtfs/otrain_2015_04_05_06.csv', encoding='utf8') as f:
        unmatched = 0
        arrival_matched = 0
        arrival_unmatched = 0
        for r in DictReader(f):
            if len(r['departure_time']) == 0:
                unmatched += 1
                continue
            found_minute = r['arrival_time'][3:5]
            expected_minute = r['Planned_Arrival'][14:]

            if 'מוצא' in r['Station_typ']:
                expected_minute = r['Planned_Depratur'][14:]
            # if len(expected_minute) == 0:
            #    expected_minute = r['Planned_Depratur'][14:]
            if found_minute == expected_minute:
                arrival_matched += 1
            else:
                arrival_unmatched += 1

    total = unmatched + arrival_matched + arrival_unmatched
    total_matched = total - unmatched
    print('unmatched', unmatched, 'of all otrain record', fp(unmatched / total))
    print('arrival match', arrival_matched, 'of all otrain record', fp(arrival_matched / total),
          'off match otrain records', fp(arrival_matched / total_matched))
    print('arrival unmatched', arrival_unmatched,
          'of all otrain record', fp(arrival_unmatched / total),
          'off match otrain records', fp(arrival_unmatched / total_matched))


def unrealised_stops():
    realised_counter = Counter()
    unrealised_counter = Counter()
    with open(r'data/otrain_gtfs/gtfs_2015_04_05_06.csv', encoding='utf8') as f:
        for r in DictReader(f):
            if r['matched'] == 'True':
                realised_counter[r['stop_name']] += 1
            else:
                unrealised_counter[r['stop_name']] += 1

    stops = set(list(realised_counter.keys()) + list(unrealised_counter.keys()))
    with open(r'data/otrain_gtfs/gtfs_unmatched_by_stop_2015_04_05_06.csv', 'w', encoding='utf8', newline='') as f:
        writer = DictWriter(f, fieldnames=['stop_name', 'realised', 'unrealised', 'unrealised_ratio'])
        writer.writeheader()
        for stop in stops:
            writer.writerow({'stop_name': stop,
                             'realised': realised_counter.get(stop, 0),
                             'unrealised': unrealised_counter.get(stop, 0),
                             'unrealised_ratio': unrealised_counter.get(stop, 0) / (realised_counter.get(stop, 0) + unrealised_counter.get(stop, 0))})




if __name__ == '__main__':
    # matched = match()
    # compare_times()
    unrealised_stops()
