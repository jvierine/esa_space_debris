#!/usr/bin/env python

import numpy as n
import matplotlib.pyplot as plt
import time
import datetime

#
# EISCAT UHF antenna coordinates:
# 05 SENTER1              7725445.727  664387.767   71.354+14.2 (pedestal foot alt + antenna height)
# 
# WGS84: 69.58649229 N 19.22592538 E, 71.354+14.2 m (pedestal foot alt + antenna height)
# distance = d - 20.0 + 5.0 m [- subreflector round trip + elevation arm length] +/- 4 m
# https://public.ccsds.org/Pubs/503x0b1c1.pdf

def date2unix(year,month,day,hour,minute,second):
    t = datetime.datetime(year, month, day, hour, minute, second)
    return(time.mktime(t.timetuple()))

def unix2date(x):
    return datetime.datetime.utcfromtimestamp(x)

def unix2datestr(x):
    return(unix2date(x).strftime('%Y-%m-%dT%H:%M:%S'))

def unix2datestrf(x):
    return("%s"%(unix2date(x).strftime('%Y-%m-%dT%H:%M:%S.%f')))

def write_ccsds(t_pulse,
                t_delay,
                norad="ERS-1",
                target="1991-050A",# cospar id for satellite
                fname="track.tdm"):
    fo=open(fname,"w")
    fo.write("CCSDS_TDM_VERS = 1.0\n")
    fo.write("   COMMENT This is a track of %s with EISCAT UHF\n"%(norad))
    fo.write("   COMMENT 929.6 MHz, time of flight, no ionospheric corrections\n")
    fo.write("   COMMENT EISCAT UHF coordinates: \n")
    fo.write("   COMMENT Position and height models, EUREF89 UTM Zone 33/NN1954\n")
    fo.write("   COMMENT Position: 7725445.727  664387.767   85.554 (ETRS89)\n")
    fo.write("   COMMENT Position: 69.58649229 N 19.22592538 E, 85.554 m (WGS84)\n")
    fo.write("   COMMENT Author(s): Juha Vierinen, Jussi Markkanen, Henry Pinedo, EISCAT.\n")
    fo.write("   COMMENT Positioning method: single pulse range-Doppler matched filter\n")
    fo.write("   COMMENT                     (1/32.0) microsecond range step.\n")
    fo.write("   CREATION_DATE       = %s\n"%(unix2datestr(time.time())))
    fo.write("   ORIGINATOR          = EISCAT\n")
    fo.write("META_START\n")
    fo.write("   TIME_SYSTEM         = UTC\n")
    fo.write("   START_TIME          = %s\n"%(unix2datestrf(t_pulse[0])))
    fo.write("   STOP_TIME           = %s\n"%(unix2datestrf(t_pulse[-1])))
    fo.write("   PARTICIPANT_1       = EISCAT_UHF_TROMSO\n")
    fo.write("   PARTICIPANT_2       = %s\n"%(target))
    fo.write("   MODE                = SEQUENTIAL\n")
    fo.write("   PATH                = 1,2,1\n")
    fo.write("   TRANSMIT_BAND       = UHF\n")
    fo.write("   RECEIVE_BAND        = UHF\n")
    fo.write("   TIMETAG_REF         = TRANSMIT\n")
    fo.write("   INTEGRATION_REF     = START\n")
    fo.write("   RANGE_MODE          = CONSTANT\n")
    fo.write("   RANGE_MODULUS       = %1.2f\n"%(128.0*20e-3))
    fo.write("   RANGE_UNITS         = s\n")
    fo.write("   DATA_QUALITY        = VALIDATED\n")
    fo.write("   CORRECTION_RANGE    = 0.0\n")
    fo.write("   CORRECTIONS_APPLIED = NO\n")
    fo.write("META_STOP\n")
    fo.write("DATA_START\n")
    for ri in range(len(t_pulse)):
        fo.write("   RANGE               = %s %1.12f\n"%(unix2datestrf(t_pulse[ri]),t_delay[ri]))
    fo.write("DATA_STOP\n")
    fo.close()

t_pulse=time.time()+n.arange(100)*0.1
t_delay=1000e3/3e8+n.random.randn(100)*1e-6

#print(unix2datestrf(n.floor(time.time())+2e-6))
write_ccsds(t_pulse,t_delay)    
