# A collection of software associated with the ESA Space Debris project at UiT

Juha Vierinen (x@mit.edu), 2016.

## PET-RDOE

Performance evaluation tool for radar determination of orbital elements. A software tool that allows evaluating the performance of a multi-static radar system for determining orbital elements. This includes radar power, aperture, locations of transmit and receive sites, as well as ionospheric radio propagation effects. 

## Tracking

The tracking programs are intended to assist in planning ranging measurements of satellites. The programs are mainly planned for use with the EISCAT steerable radars. There is also a program, which will allow the results to be exported into CCSDS format for ingestion with the ESA orbital elements determination program. 

Calculate passes:

```
python sat_predict.py -0 "2016/09/06 02:00:00" -1 "2016/09/06 14:00:00"
ERS-1 best pass 2016/9/6 02:21:04 az 290.59 el 88.63 r 757.66
2016/9/6 02:18:32 - 2016/9/6 02:23:37 duration 5.08 min peak_el 88.63
2016/9/6 03:58:11 - 2016/9/6 04:01:30 duration 3.32 min peak_el 38.97
2016/9/6 08:53:17 - 2016/9/6 08:54:27 duration 1.17 min peak_el 30.88
2016/9/6 10:29:59 - 2016/9/6 10:34:45 duration 4.77 min peak_el 62.78
2016/9/6 12:09:28 - 2016/9/6 12:13:48 duration 4.33 min peak_el 50.24
ERS-2 best pass 2016/9/6 11:26:13 az 246.53 el 86.48 r 521.33
2016/9/6 02:05:39 - 2016/9/6 02:09:03 duration 3.40 min peak_el 65.60
2016/9/6 03:39:53 - 2016/9/6 03:42:14 duration 2.35 min peak_el 38.92
2016/9/6 09:52:02 - 2016/9/6 09:53:18 duration 1.27 min peak_el 32.03
2016/9/6 11:24:27 - 2016/9/6 11:28:00 duration 3.55 min peak_el 86.48
```

```
python plan_pass.py -0 "2016/9/6 02:18:32" -1 "2016/9/6 02:23:37" -n ERS-1 -p 3
2016/9/6 02:18:32
2016/9/6 02:23:37
time between positions 101.67 s
Dwell 10.00 s, setup 300.00 s
at 2016/9/6 02:13:32 go to 24.87 30.19
at 2016/9/6 02:18:42 go to 23.49 62.77 antenna move_time 16.29 available_time 91.67
at 2016/9/6 02:20:23 go to 209.26 63.02 antenna move_time 87.11 available_time 91.67
at 2016/9/6 02:22:04 go to 207.84 30.32 antenna move_time 16.35 available_time 91.67
```
