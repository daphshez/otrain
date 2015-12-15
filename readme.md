# Analysis of Israel Open Train 

Analysis of data of the [Open Train project](http://otrain.org/) 

[2013-2014 data on github](https://github.com/hasadna/OpenTrainCommunity)

[2014-2015 data](http://otrain.org/files/xl/)

## Plan

* ~~get new data from train (if available) or old one (if not)~~
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
* ~~fix the GTFS download script~~
* load and compare 2014 data
* design a measure for train latency based on daily number of passengers
...Some kind of balance for time of day
* chart delay along route
* are all trips with the same train number basically the same?
* do the 60/90-seconds stop really cause delays?
* are all otrain data that aren't matched to gtfs non planned to non commercial stops?
* Why does sometimes (very few) planned time in otrain data != gtfs time?



## Some insights 
### (Planned stop == False) is equivalent to (planned stop time == 0)
2013-2014 data didn't have a flag for whether the train was supposed to stop at station at all.

Originally I suggested to cross-validate against GTFS data to achieve that.

However 2014-2015 data has a "planned stop" flag. It seems that its value can be precisely predicated
from the planned time at station. 

### GTFS cross-validation still needed 
see https://github.com/daphshez/otrain/blob/master/irw_gtfs.md

### 60-seconds stops never happen
This is according to the analysis of 2015q2 data. 

The most common values by far for stop time (when stop is planned at all) are 60 and 120 seconds. 

While 120 seconds seems reasonable, 60 seconds seems to be by far to short.

For planned 120 seconds stops, actual stop value statistics are:
```
  count    13626.000000
  mean       121.776897
  std         48.929106
  min         16.000000
  25%         92.000000
  50%        112.000000
  75%        140.000000
  max       1712.000000
```

For planned 60 second stops, actual stop value stations are:
```
  count    33061.000000
  **mean        95.752246**
  std         47.009714
  min          6.000000
  25%         62.000000
  **50%         90.000000**
  75%        113.000000
  max       1726.000000
```

An intesrting question would be whether delays are correlated with these longer stop times.
