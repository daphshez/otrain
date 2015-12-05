# Analysis of Israel Open Train 

Analysis of data of the [Open Train project](http://otrain.org/)



## Plan

* ~~get new data from train (if available) or old one (if not): http://otrain.org/files/xl/~~
* ~~clean the excel file: remove empty rows. english column names.~~
* ~~try to load the whole excel file~~
* ~~add time at station col~~
* ~~time in station for actual stopped True and Falses~~
* ~~more data cleanup:~~
 * ~~Remove מוצא תפעולי ויעד תפעולי~~
 * ~~On מוצא מחסחרי, remove arrival time~~
 * ~~on יעד מסחרי, remove departure time~~
 * ~~If time in station is longer than 80000, subtract number of seconds in day~~
* ~~histogram of time in station~~
* ~~Time at station planned to actual~~
* ~~histogram for actual stop length, grouped by planned~~
* fix the GTFS download script
* load and compare 2014 data
* design a measure for train latency based on daily number of passengers


## GTFS cross-validation
**GTFS cross-validation:** The original motivation was to understand whether the train was supposed to stop at the station at all. It appears that this isn't needed because this is identical to checking time_at_station = 0.

However according Eran's mail from 4/11, it's possible that the planned departure time isn't the advertised depature time. This needs to be checked against the GTFS.

http://192.241.154.128/gtfs-data/