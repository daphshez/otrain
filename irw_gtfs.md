# Some partial conclusions about Israel Railway GTFS data

## First, a general overview of the GTFS tables
![GTFS schema](https://raw.githubusercontent.com/daphshez/otrain/master/data/gtfs/gtfs.jpg)

## disclaimer
This work was done on irw_gtfs.zip files which were available until July 15 2015.

I haven't looked yet at the railway data included in the full israel gtfs data (which is the only
one available since that date).

## Use the latest available file
* A daily GTFS file contains data for the next two months.
* Some times there's a change in plans. For example, according to early June 2015 files, trip 010715_00053 was
supposed to leave at 23:07 from Tel-Aviv Center. But in files from June 22 forward, this trip starts
instead in Tel-Aviv University at 23:03 and not stop in Tel-Aviv Center.
* So for most use cases, it's best to use the file published the nearest to the trip we are interested in.

## Not normalised
* GTFS allows to define repeating trips. For example, if you have a train going from Nahariya to Natbag
every weekday at 7:09, this could have been described using one trip record, with the appropriate
use of the Calendar record to define dates and days of week.
* irw_gtfs doesn't make use of this normalisation option. Instead, every single train trip (every departure)
is described using a Trips table record.
* (but could this be deduced from trip id?)

## Joining GTFS and open train data
* If you join the stop_times table in the gtfs to the open train data, you get the arrival and departure
time as they were advertised to the public.
* The join is based on three fields: train date, train number and stop id
  * these fields appear as is in the open train data
  * in the gtfs, train date and train number are coded together in the trip_id field (e.g. 010815_07001 means train 7001 of the 1/8/15)

## Some initial results for the join
Joining the data for 2015q2, here's some finds:
* In most cases, the advertised time (gtfs time) of arrival and departure is identical (the only station where
this sometimes doesn't hold is Tel-Aviv Center.)
* in 99.5% of cases, the advertised **departure** time is arrival time in otrain data. This
may explain why what looks like early departure in otrain data isn't perceived this way by passengers.
* 99.4% of the advertised stops appear in otrain data. Which also means 0.6% of the stops (2266 out of 382119
planned stops) do not appear in the otrain data. In the following stations it happens in more than 1% of the 
stops:
```
  stop_name	                ratio
  Dimona                    2.94%
  Bet Shemesh               1.61%
  Herzliyya                 1.29%
  Jerusalem Malha           1.23%
  Jerusalem Biblical Zoo    1.17%
  Kesariyya - Pardes Hanna  1.14%
  Ramla                     1.05%
```
  (however could this be offset by unmatch otrain data?)