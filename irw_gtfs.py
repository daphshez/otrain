__author__ = 'Daphna'

from collections import namedtuple, defaultdict
from io import TextIOWrapper
from csv import DictReader, DictWriter
from zipfile import ZipFile
import os

Route = namedtuple('Route', 'route_id route_long_name')
# it seems that all services in IRW.zip have a single day
Service = namedtuple('Service', 'service_id day start_date end_date')
Stop = namedtuple('Stop', 'stop_id stop_name')
# stop is a stop object
StopTime = namedtuple('StopTime', 'trip_id arrival_time departure_time stop stop_sequence')
# stops is a list of StopTime
Trip = namedtuple('Trip', 'route service trip_id trip_headsign direction_id stops')
# all data
Schedule = namedtuple('Schedule', 'routes services stops trips date_published')


### utils
def flatten(list_of_lists):
    return [item for list in list_of_lists for item in list]


def group_by(list, key):
    d = {}
    for item in list:
        d.setdefault(key(item), []).append(item)
    return d


def merge_dicts(d1, d2):
    d = d1.copy()
    d.update(d2)
    return d


###


def load_schedule(zip_name):
    def calendar_get_day(r):
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        values = [r[day] for day in days_of_week]
        return values.index('1')

    def load_stop_times(reader):
        stop_times = defaultdict(lambda: [])
        for r in reader:
            stop = stops[r['stop_id']]
            # trip_id arrival_time departure_time stop stop_sequence
            stop_time = StopTime(r['trip_id'], r['arrival_time'], r['departure_time'], stop, r['stop_sequence'])
            stop_times[r['trip_id']].append(stop_time)
        return stop_times

    def make_trip(r):
        route = routes[r['route_id']]
        service = services[r['service_id']]
        stops = stop_times[r['trip_id']]
        return Trip(route, service, r['trip_id'], r['trip_headsign'], r['direction_id'], stops)

    with ZipFile(zip_name) as z:
        with z.open('routes.txt') as routes_file:
            reader = DictReader(TextIOWrapper(routes_file, 'utf-8-sig'))
            routes = {r['route_id']: Route(r['route_id'], r['route_long_name']) for r in reader}

        with z.open('calendar.txt') as services_file:
            reader = DictReader(TextIOWrapper(services_file, 'utf-8-sig'))
            services = {r['service_id']: Service(r['service_id'],
                                                 calendar_get_day(r),
                                                 r['start_date'], r['end_date']) for r in reader}

        with z.open('stops.txt') as stops_file:
            reader = DictReader(TextIOWrapper(stops_file, 'utf-8-sig'))
            stops = {r['stop_id']: Stop(r['stop_id'], r['stop_name']) for r in reader}

        with z.open('stop_times.txt') as stop_times_file:
            reader = DictReader(TextIOWrapper(stop_times_file, 'utf-8-sig'))
            stop_times = load_stop_times(reader)

        with z.open('trips.txt') as trips_file:
            reader = DictReader(TextIOWrapper(trips_file, 'utf-8-sig'))
            trips = [make_trip(r) for r in reader]

    date_published = min(trip.service.start_date for trip in trips)
    return Schedule(routes, services, stops, trips, date_published)


def group_trips_by_date(schedule):
    """This is tailor-made of IRW GTFS, where there's a 1-1 relation between trips and services"""
    by_date = defaultdict(lambda: [])
    for trip in schedule.trips:
        by_date[trip.service.start_date].append(trip)
    return by_date


def merge_schedules(schedule1, schedule2):
    """Merge to schedule objects.
     Result won't contain the services field (will have None instead).
     If there's a date that appears in both schedules, trips from schedule1 will be used"""
    # Schedule = namedtuple('Schedule', 'routes services stops trips')
    routes = merge_dicts(schedule2.routes, schedule1.routes)
    services = None
    stops = merge_dicts(schedule2.stops, schedule1.stops)
    # order is important because we want schedule1 trip to override schedule2
    by_date = merge_dicts(group_trips_by_date(schedule2), group_trips_by_date(schedule1))
    # he he nested list comprehension
    trips = flatten(by_date.values())
    return Schedule(routes, services, stops, trips)


def load_schedules(zip_names):
    """
    Load scheduled data from all the input files.
    Data for each date will only be loaded from the first file in which the date appears, so order
     is important
    """
    schedule = load_schedule(next(zip_names))
    for zip_name in zip_names:
        schedule = merge_schedules(schedule, load_schedule(zip_name))
    return schedule


def merge_gtfs(zip_files, output_folder, n_days=None, date_range=None):
    # fields that are going to be used
    fields = ['trip_id', 'date', 'route_id', 'route_long_name', 'trip_headsign', 'stop_id', 'stop_name',
              'arrival_time', 'departure_time', 'stop_sequence', 'gtfs_date']

    def make_row(schedule, trip, stop):
        return {'trip_id': trip.trip_id,
                'date': trip.service.start_date,
                'route_id': trip.route.route_id,
                'route_long_name': trip.route.route_long_name,
                'trip_headsign': trip.trip_headsign,
                'stop_id': stop.stop.stop_id,
                'stop_name': stop.stop.stop_name,
                'arrival_time': stop.arrival_time,
                'departure_time': stop.departure_time,
                'stop_sequence': stop.stop_sequence,
                'gtfs_date': schedule.date_published}

    def make_output_filename():
        output_file_name = 'stops'
        if date_range is not None:
            output_file_name += '_' + date_range[0] + '_' + date_range[1]
        if n_days is not None:
            output_file_name += '_' + str(n_days)
        output_file_name += '.txt'
        return os.path.join(output_folder, output_file_name)


    dates_done = set()
    with open(make_output_filename(), 'w', encoding='utf8', newline='') as f:
        writer = DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for zip_file in zip_files:
            print(zip_file)
            schedule = load_schedule(zip_file)
            by_date = group_by(schedule.trips, lambda trip: trip.service.start_date)
            # prepare the list of dates to writer
            dates_to_use = [date for date in by_date.keys() if date not in dates_done and
                            (date_range is None or date >= date_range[0] and date <= date_range[1])]
            print("Adding ", len(dates_to_use), "day")
            dates_done.update(dates_to_use)

            for date in reversed(sorted(dates_to_use)):
                for trip in by_date[date]:
                    for stop in trip.stops:
                        writer.writerow(make_row(schedule, trip, stop))

                if n_days is not None and len(dates_done) >= n_days:
                    return


if __name__ == '__main__':
    import re
    folder = 'data/gtfs/raw'
    zip_files = [os.path.join(folder, f) for f in os.listdir(folder) if re.match('^2015_0[4-6].*zip', f) is not None]
    merge_gtfs(reversed(zip_files), 'data/gtfs/merged', date_range=('20150401', '20150630'))