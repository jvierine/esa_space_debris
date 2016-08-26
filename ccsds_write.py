#!/usr/bin/env python

import numpy as n
import matplotlib.pyplot as plt
import time
import datetime

def date2unix(year,month,day,hour,minute,second):
    t = datetime.datetime(year, month, day, hour, minute, second)
    return(time.mktime(t.timetuple()))

def unix2date(x):
    return datetime.datetime.utcfromtimestamp(x)

def unix2datestr(x):
    return(unix2date(x).strftime('%Y-%m-%dT%H:%M:%S'))

def unix2datestrf(x):
    frac=int((x-n.floor(x))*100000)
    return("%s.%d"%(unix2date(x).strftime('%Y-%m-%dT%H:%M:%S'),frac))

def write_ccsds(t_pulse,
                t_delay,
                norad="ERS-1",
                target="1991-050A",# cospar id for satellite
                fname="track.tdm"):
    fo=open(fname,"w")
    fo.write("CCSDS_TDM_VERS = 1.0\n")
    fo.write("COMMENT This is a track of %s with EISCAT UHF\n"%(norad))
    fo.write("CREATION_DATE = %s\n"%(unix2datestr(time.time())))
    fo.write("ORIGINATOR = EISCAT\n")
    fo.write("META_START\n")
    fo.write("TIME_SYSTEM = UTC\n")
    fo.write("START_TIME = %s\n"%(unix2datestrf(t_pulse[0])))
    fo.write("STOP_TIME = %s\n"%(unix2datestrf(t_pulse[-1])))
    fo.write("PARTICIPANT_1 = EISCAT_UHF_TROMSO\n")
    fo.write("PARTICIPANT_2 = %s\n"%(target))
    fo.write("MODE = SEQUENTIAL\n")
    fo.write("PATH = 1,2,1\n")
    fo.write("TRANSMIT_BAND = UHF\n")
    fo.write("RECEIVE_BAND = UHF\n")
    fo.write("TIMETAG_REF = TRANSMIT\n")
    fo.write("INTEGRATION_REF = START\n")
    fo.write("RANGE_MODE = CONSTANT\n")
    fo.write("RANGE_MODULUS = 1.0E7\n")
    fo.write("RANGE_UNITS = s\n")
    fo.write("DATA_QUALITY = VALIDATED\n")
    fo.write("CORRECTION_RANGE = 0.0\n")
    fo.write("CORRECTIONS_APPLIED = NO\n")
    fo.write("META_STOP\n")
    fo.write("DATA_START\n")
    for ri in range(len(t_pulse)):
        fo.write("RANGE = %s %1.11f\n"%(unix2datestrf(t_pulse[ri]),t_delay[ri]))
    fo.write("DATA_STOP\n")
    fo.close()

t_pulse=time.time()+n.arange(100)*0.1
t_delay=1000e3/3e8+n.random.randn(100)*1e-6
write_ccsds(t_pulse,t_delay)    
