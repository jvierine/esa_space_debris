#!/usr/bin/env python
#
# Juha Vierinen, 2016
#
# - plan a schedule for tracking targets, plot the schedule
# - identify conflicts (overlapping tracks) and resolve them
# - write an elan file with appropriate commands (AT, pointdir)
#
# 
import ephem, sys, math
import os, errno, time 
import matplotlib.pyplot as plt
import numpy as n
import sat_elements as se
from optparse import OptionParser
import plan_pass as pp

# automatic fetching of TLE from space-track.org
def plot_predicts_overview(predicts):
    for p in predicts:
        plt.plot(p["hv"],p["el"],label=p["name"])
    plt.legend(loc="lower right")
    plt.title("Hours after %s"%(predicts[0]["t0"]))
    plt.ylim([0,90])
    plt.axhline([30.0])
    plt.savefig("plots/overview.png")

    

def get_track(norad_id,
              startd = ephem.Date("2016/09/01 00:00:00"),
              endd = ephem.Date("2016/09/01 00:00:00"),
              latitude="69:35:11.0",
              longitude="19:13:38.0",
              altitude=86.0,
              dwell_time=20.0,
              el_thresh=30.0):

    obs = ephem.Observer()
    obs.lat = latitude
    obs.long = longitude
    obs.elevation = altitude
    dt_sec = int((endd-startd)/ephem.second)

    p0=[]
    p1=[]
    pass_els=[]
    pass_el=0.0
    pass_on=False
    
    target=se.get_tle(norad_id)
    sat = ephem.readtle(target["name"],target["tle1"],target["tle2"])
    rv=[]
    hv=[]
    tv=[]
    elv=[]
    azv=[]
    maxel=-100
    maxaz=-100
    maxr=-100
    maxt=0

    # look a little over one day in advance 1 sec steps
    for i in range(0,dt_sec,1):
        #    obs.date = 
        obs.date = startd + float(i)*ephem.second
        sat.compute(obs)
        el = 360.0*float(sat.alt)/2.0/math.pi
        az = 360.0*float(sat.az)/2.0/math.pi 
        r = float(sat.range)
        alt = float(sat.elevation)
        vel = float(sat.range_velocity)
        sublat = 360.0*float(sat.sublat)/2.0/math.pi
        sublong = 360.0*float(sat.sublong)/2.0/math.pi
        azv.append(az)
        elv.append(el)
        rv.append(r)
        tv.append(obs.date)
        hv.append(float(i)/(60.0*60.0))
        if pass_on == False and el > el_thresh:
            p0.append(obs.date)
            pass_el=el_thresh
            pass_on = True
        if pass_on == True and el < el_thresh:
            p1.append(obs.date)
            pass_els.append(pass_el)
            pass_on=False
        if pass_on == True and el > el_thresh:
            if el > pass_el:
                pass_el = el
        if el > maxel:
            maxel=el
            maxaz=az
            maxelt=obs.date
            maxr=r

    print("%s best pass %s az %1.2f el %1.2f r %1.2f"%(target["name"],maxelt,maxaz,maxel,maxr/1e3))
    return({"hv":hv,"az":azv,"el":elv,"name":target["name"],"peakel":maxel,"p0":p0,"p1":p1,"peak_el":pass_els,"t0":startd})

def calc_predicts(targets,t0,t1):
    predicts=[]
    for norad_id in targets:
        t=get_track(norad_id,startd=ephem.Date(t0),endd=ephem.Date(t1))
        predicts.append(t)
    plot_predicts_overview(predicts)
    return(predicts)

parser = OptionParser()

parser.add_option("-0", "--t0", dest="t0", default="2016/01/01 00:00:00",
                  help="Start of track")

parser.add_option("-1", "--t1", dest="t1", default="2016/01/01 00:00:00",
                  help="End of track")

parser.add_option("-a", "--lat", dest="lat", default="69:35:11.0",
                  help="Latitude")

parser.add_option("-b", "--lon", dest="lon", default="19:13:38.0",
                  help="Longitude")

parser.add_option("-p", "--n_pos", dest="n_pos", default=4,
                  help="Number of pointing positions.")

parser.add_option("-d", "--dwell_time", dest="dwell_time", default=5.0,
                  help="Amount of time to spend on target after target has passed.")

parser.add_option("-t", "--targets", dest="targets", default="27386,23560,21574,26958,39162,38086",
                  help="Targets to track, comma separated list of NORAD catalog numbers")

parser.add_option("-z", "--debug", dest="debug", action="store_true",
                  help="Test antenna movement using SYNC")
parser.add_option("-c", "--clear_cache", dest="clear_cache", action="store_true",
                  help="Clear TLE cache")

(o, args) = parser.parse_args()

if o.clear_cache:
    se.clear_cache()
pass_t0=[]
pass_names=[]
lat=o.lat#print(o.lat)
lon=o.lon

targets=o.targets.split(",") # se.targets
print(targets)
tracklets=[]
predicts=[]
t0s=[]
t1s=[]
results=[]

calc_predicts(targets,o.t0,o.t1)

for norad_id in targets:
    # get all passes for target
    t=get_track(norad_id,startd=ephem.Date(o.t0),endd=ephem.Date(o.t1))
    for i in range(len(t["p0"])):
        pass_t0.append(t["p0"][i])
        print("%s - %s duration %1.2f min peak_el %1.2f" %(t["p0"][i],t["p1"][i],(t["p1"][i]-t["p0"][i])/ephem.minute,t["peak_el"][i]))
        tl=pp.plan(norad_id, t["p0"][i], t["p1"][i], lat, lon, o.dwell_time, debug=o.debug)
        tracklets.append(tl)
        t0s.append(tl["t0"])
        t1s.append(tl["t1"])

t0s=n.array(t0s)
t1s=n.array(t1s)
idx=n.argsort(t0s)
prev_endt=-1

if o.debug:
    fo=file("turtle_and_rabbit_debug.elan","w")
else:
    fo=file("turtle_and_rabbit.elan","w")
fo.write("MAIN { args } {\n")
fo.write("    callblock turtle_and_rabbit\n")
fo.write("    after 86400 stopexperiment\n")
fo.write("}\n")

fo.write("BLOCK turtle_and_rabbit { args } {\n")
for ii,i in enumerate(idx):
    overlap=""

    if ii>0:
        prev_endt=t1s[idx[ii-1]]
    if (i>0) and (ii > 0) and t0s[idx[ii]] < prev_endt:
        overlap="overlapping previous tracklet"

#    fo.write("BLOCK point_and_stare { args } {\n")
    fo.write("DISP -hms. \"%s t0 %s t1 %s %s\"\n"%(tracklets[i]["name"],ephem.Date(t0s[i]),ephem.Date(t1s[i]),overlap))
    for ti in range(len(tracklets[i]["track_points"])):
        if tracklets[i]["point_t"][ti] > prev_endt:
            fo.write("%s\n"%(tracklets[i]["track_points"][ti]))
        else:
            fo.write("# overlapping with previous track, skipping %s\n"%(tracklets[i]["track_points"][ti]))
    fo.write("\n\n")
fo.write("}")
fo.close()

#    plt.plot(t["hv"],t["el"],label=t["name"])

#plt.xlabel("Time (UTC)")
#plt.ylabel("Elevation (deg)")
#plt.legend()#prop={'size':6})
#plt.axhline(30)
#plt.ylim([0,90])

#plt.show()

