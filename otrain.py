__author__ = 'Daphna'

from csv import DictReader, DictWriter
import csv
from zipfile import ZipFile
from io import TextIOWrapper


def load_hebrew_name_dictionary():
    lines = """route_id,name
51,נהריה - מודיעין מרכז
52,נהריה - באר שבע מרכז
53,נהריה - חוף הכרמל
54,בנימינה - אשקלון
55,הוד השרון-שדרות
56,נתניה-הראשונים
57,הרצליה- ירושלים מלחה
58,באר שבע צפון-דימונה
59,חיפה מרכז - בש מרכז
60,נהריה - נתבג
""".split('\n')
    return {r['name']: r['route_id'] for r in DictReader(lines)}


def load_2015q3():
    print("Loading otrain data for 2015q3")
    di = {'מתוכננת': True, 'לא מתוכננת': False}
    heb_route_names = load_hebrew_name_dictionary()

    def skip_record(r):
        return 'תפעולי' in r['Station_typ']

    def fix_record(r):
        r['Planned'] = di[r['Planned']]
        if 'מוצא' in r['Station_typ']:
            r['Timestamp_For_Match'] = r['Planned_Depratur'][11:] + ":00"
        else:
            # gtfs uses hours >= 24 for trips that continue after midnight
            timestamp = r['Planned_Arrival'][11:]
            if r['Planned_Arrival'][:10].strip() != r['Train_Date']:
                timestamp =  str(int(timestamp[:2]) + 24) + timestamp[2:]
            r['Timestamp_For_Match'] = timestamp + ":00"
        # reformat train date to match gtfs format
        r['Train_Date'] = r['Train_Date'][6:] + r['Train_Date'][3:5] + r['Train_Date'][:2]
        r['route_id'] = heb_route_names.get(r['Route_Description'], '')
        return r

    with ZipFile(r'data\otrain\2015_04_05_06.zip') as z:
        with z.open('2015_04_05_06.txt') as f:
            reader = DictReader(TextIOWrapper(f, 'utf-8'), delimiter='\t', quoting=csv.QUOTE_NONE)
            return [fix_record(r) for r in reader if not skip_record(r)]


def match_otrain_gtfs(gtfs_file_name, otrain_data):
    otrain_fields = "Train_Date,Train_Number,Planned,Station_number,Station_Description,Station_Order,Route_Description,Station_typ,Planned_Stop,Actual_Stop,Planned_Depratur,Actual_Departure,Planned_Arrival,Actual_Arrival".split(',')
    extra_fields = "trip_id,route_id,arrival_time,departure_time,stop_sequence,gtfs_date".split(',')

    # read merged_gtfs_file (which is the output of merge_gtfs)
    # index by date, route_id, stop_id, arrival_time
    print("Loading gtfs data from", gtfs_file_name)
    gtfs_lines = [line for line in open(gtfs_file_name)]
    # gtfs_data is a mapping from the key (date, route_id, stop_id, arrival_time) to a pair of the line and the line
    # number. Line number helps to easily find out later which gtfs lines were succesfully matched.
    gtfs_data = {(r['date'], r['route_id'], r['stop_id'], r['arrival_time']): (r, i)
                 for (i, r) in enumerate(DictReader(gtfs_lines))}

    gtfs_line_to_train_number = {}

    def match(r):
        key = r['Train_Date'], r['route_id'], r['Station_number'], r['Timestamp_For_Match']
        gtfs_record = gtfs_data.get(key, None)
        if gtfs_record:
            gtfs_line_to_train_number[gtfs_record[1]] = r['Train_Number']
            return gtfs_record[0]

    def enrich(r, gtfs_record):
        if gtfs_record:
            for key in extra_fields:
                r[key] = gtfs_record[key]
        return {key: r.get(key, '') for key in otrain_fields + extra_fields}




    # write the matched record
    print("Matching records and writing updated otrain data")
    with open(r'data/otrain_gtfs/otrain_2015_04_05_06.csv', 'w', encoding='utf8', newline='') as f:
        writer = DictWriter(f, fieldnames=otrain_fields+extra_fields)
        writer.writeheader()
        for r in otrain_data:
            writer.writerow(enrich(r, match(r)))

    # write a copy of the gtfs file with an extra field to whether to record was used
    print("Writing updated gtfs")
    with open(r'data/otrain_gtfs/gtfs_2015_04_05_06.csv', 'w', encoding='utf8') as f:
        f.write( gtfs_lines[0].strip() + ',train_number\n' )
        for i, line in enumerate(gtfs_lines[1:]):
            line = line.strip() + "," + gtfs_line_to_train_number.get(i, "-1") + "\n"
            f.write(line)

    # print some stats :-)
    print('otrain:', len(otrain_data))
    print('gtfs:', len(gtfs_lines))
    print('matched:', len(gtfs_line_to_train_number), len(gtfs_line_to_train_number) / len(gtfs_data), 'of gtfs records')


if __name__ == '__main__':
    matched = match_otrain_gtfs('data/gtfs/merged/stops_20150401_20150630.txt', load_2015q3())






