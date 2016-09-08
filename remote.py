#!/usr/bin/env python

import ephem, sys, math
import os, errno, time 
import matplotlib.pyplot as plt
import numpy as n
import sat_elements as se

date = ephem.Date("2016/09/06 03:50:15")
# proba-1, 
norad_id="26958"

# avum r/b
date = ephem.Date("2016/09/06 05:29:54")
norad_id="38086"

coords={}
coords["kiruna"]= {"site":"kiruna","lat":"67:51:38","lon":"20:26:07","alt":418.0}
coords["sodankyla"]={"site":"sodankyla","lat":"67:21:49","lon":"26:37:37","alt":197.0}


sites=["kiruna","sodankyla"]
for site in sites:
    obs = ephem.Observer()
    obs.lat = coords[site]["lat"]
    obs.long = coords[site]["lon"]
    obs.elevation = coords[site]["alt"]


    target=se.get_tle(norad_id)
    sat = ephem.readtle(target["name"],target["tle1"],target["tle2"])

    obs.date = date
    sat.compute(obs)

    el = 360.0*float(sat.alt)/2.0/math.pi
    az = 360.0*float(sat.az)/2.0/math.pi 

    print("%s %s %s az %1.2f el %1.2f"%(site,obs.date,target["name"],az,el))



