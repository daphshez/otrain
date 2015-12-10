__author__ = 'Daphna'

from collections import namedtuple, defaultdict
from csv import DictReader
from zipfile import ZipFile

Route = namedtuple('Route', 'route_id route_long_name')
# it seems that all services in IRW.zip have a single day
Service = namedtuple('Service', 'service_id day start_date end_date')
Stop = namedtuple('Stop', 'stop_id stop_name')
# stop is a stop object
StopTime = namedtuple('StopTime', 'trip_id arrival_time departure_time stop stop_sequence')
# stops is a list of StopTime
Trip = namedtuple('Trip', 'route service trip_id trip_headsign direction_id stops')


def load(zip_name):
    def calendar_get_day(row):
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        values = [row[day] for day in days_of_week]
        return values.index('1')

    def load_stop_times(reader):
        stop_times = defaultdict(lambda: [])
        for r in reader:
            stop = stops[row['stop_id']]
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
            reader = DictReader(routes_file)
            routes = {r['route_id']: Route(r['route_id'], r['route_long_name']) for r in reader}

        with z.open('calendar.txt') as services_file:
            reader = DictReader(services_file)
            services = {r['service_id']: Service(r['service_id'],
                                                 calendar_get_day(r),
                                                 r['start_date'], r['end_date']) for r in reader}

        with z.open('stops.txt') as stops_file:
            reader = DictReader(stops_file)
            stops = {r['stop_id']: Stop(r['stop_id'], r['stop_name']) for r in reader}

        with z.open('stop_times.txt') as stop_times_file:
            reader = DictReader(stop_times_file)
            stop_times = load_stop_times(reader)

        with z.open('trips.txt') as trips_file:
            reader = DictReader(trips_file)
            return [make_trip(r) for r in reader]