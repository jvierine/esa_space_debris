#!/usr/bin/env python

import ephem, sys, math
import os, errno, time 
import matplotlib.pyplot as plt
import numpy as n
from optparse import OptionParser
import sat_elements as se
import datetime
import h5py

#
# UHF azimuth limits
# 90 to 630
# 

def move_time(az0,az1,el0,el1,az_speed=80.0/60.0,el_speed=80.0/60.0):
    dang=n.abs(180.0*n.angle((n.exp(1j*n.pi*az1/180.0)/n.exp(1j*n.pi*az0/180.0)))/n.pi)
    return(n.max([dang/az_speed,n.abs(el1-el0)/el_speed]))

def find_n_points(pass_length,total_time,antenna_speed=80.0/60.0,dwell_time=20.0):
    n=0
    while (pass_length/antenna_speed + dwell_time*n) < total_time:
        n+=1
    return(n)

def track(norad_id,
          startd = ephem.Date("2016/09/01 00:00:00"),
          endd = ephem.Date("2016/09/01 00:00:00"),
          latitude="69:35:11.0",
          longitude="19:13:38.0",
          altitude=86.0,
          dwell_time=20.0):

    obs = ephem.Observer()
    obs.lat = latitude
    obs.long = longitude
    obs.elevation = altitude
    dt_sec = int((endd-startd)/ephem.second)

    target=se.get_tle(norad_id)
    sat = ephem.readtle(target["name"],target["tle1"],target["tle2"])
    rv=[]
    hv=[]
    tv=[]
    tv_sec=n.zeros(int(dt_sec))
    elv=[]
    azv=[]
    maxel=-100
    maxaz=-100
    maxr=-100
    maxt=0
    
    obs.date = startd
    sat.compute(obs)
    el_prev = 360.0*float(sat.alt)/2.0/math.pi
    az_prev = 360.0*float(sat.az)/2.0/math.pi 
    antenna_movement_time=0.0
    time_available=-2.0*dwell_time

    dt_avg=float((endd-startd)/ephem.second)/5.0

    point_t=[]
    point_r=[]
    point_dt=[]
    point_az=[]
    point_el=[]

    # look a little over one day in advance 1 sec steps
    for i in range(0,int(dt_sec),1):
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
        tv_sec[i]=i
        azv.append(az)
        elv.append(el)
        rv.append(r)
        tv.append(obs.date)
        hv.append(float(i)/(60.0*60.0))

        # figure out where next position can be
        antenna_movement_time+=move_time(az,az_prev,el,el_prev,az_speed=60.0/60.0,el_speed=60.0/60.0)
        az_prev=az
        el_prev=el

        if el > maxel:
            maxel=el
            maxaz=az
            maxelt=obs.date
            maxr=r

    n_points = 0
    while (dt_sec - (antenna_movement_time + 6.0*dwell_time*(n_points+1))) > 0.0:
        print("%d antenna move %1.2f dt %1.2f"%(n_points,antenna_movement_time,dt_sec-antenna_movement_time-2.0*dwell_time*n_points))
        n_points += 1
    if n_points < 2:
        n_points = 2
    spacing=float(dt_sec)/float(n_points)

    for i in range(n_points+1):
        obs.date = startd + float(i)*ephem.second*int(spacing)
        sat.compute(obs)
        el = 360.0*float(sat.alt)/2.0/math.pi
        az = 360.0*float(sat.az)/2.0/math.pi 
        r = float(sat.range)
        alt = float(sat.elevation)
        vel = float(sat.range_velocity)
        sublat = 360.0*float(sat.sublat)/2.0/math.pi
        sublong = 360.0*float(sat.sublong)/2.0/math.pi
        point_t.append(obs.date)
        point_dt.append(spacing)
        point_az.append(az)
        point_r.append(r)
        point_el.append(el)
#        print("pointdir %1.2f %1.2f"%(az,el))

    point_az=n.array(point_az)
    point_el=n.array(point_el)
    point_dt=n.array(point_dt)
    point_r=n.array(point_r)
    return({"hv":hv,"az":azv,"el":elv,"norad_id":norad_id,
            "name":target["name"],"norad_id":norad_id,"peakel":maxel,"point_t":point_t,"point_az":point_az,"point_el":point_el,"point_r":point_r,"dt":point_dt})


# dwell_time is move antenna n sec after target has passed the point
def points_to_plan(t, 
                   setup_time=5*60, 
                   dwell_time=20.0,
                   bp_az=85.0,
                   bp_el=45.0,
                   debug=False):

    date0=ephem.Date("2016/1/1 00:00:00")
    date_ut0=ephem.Date("1970/1/1 00:00:00")
    secs=[]
    utsecs=[]
    for ti in t["point_t"]:
        secs.append((ti-date0)/ephem.second)
        utsecs.append((ti-date_ut0)/ephem.second)
    secs=n.array(secs)
    utsecs=n.array(utsecs)
    ho= h5py.File("data/%d.h5"%(secs[0]),"w")
    ho["eiscat_secs"]=secs
    ho["ut_secs"]=utsecs
    ho["r"]=t["point_r"]
    ho["name"]=t["name"]
    ho["norad_id"]=t["norad_id"]
    ho["cospar_id"]=se.get_cospar(t["norad_id"])
    ho.close()
    
    track_points=[]
    point_ts=[]
    azs=[]
    els=[]
#    print("# Dwell %1.2f s, setup %1.2f s"%(dwell_time,setup_time))
    startt=t["point_t"][0]-ephem.second*setup_time
    colors=[]
    slack=[]
    point_ts.append(startt)
    printant="DISP -hms. [getdirection -all]"
    sync_str=""
    if debug:
        at_str="# AT \"%s\""%(ephem.Date(startt).datetime())
    else:
        at_str="AT \"%s\""%(ephem.Date(startt).datetime())
    if debug:
        sync_str="SYNC %1.2f\nDISP -hms. \"Antenna should have stopped by now!\"\n%s"%(setup_time-dwell_time,printant)
    else:
        sync_str=""
    tstr="%s\npointdirection %1.2f %1.2f\nupar 17 %s\nupar 18 %1.2f\nupar 19 %1.2f\nDISP -hms. \"at %s, satellite will be at %1.2f %1.2f\"\n%s\n"%(
        at_str,
        t["point_az"][0],
        t["point_el"][0],
        t["norad_id"],
        t["point_az"][0],
        t["point_el"][0],
        t["point_t"][0],
        t["point_az"][0],
        t["point_el"][0],
        sync_str)

    track_points.append(tstr)
    colors.append("green")
    slack.append(setup_time)

    azs.append(t["point_az"][0])
    els.append(t["point_el"][0])

    available_time=n.diff(n.array(t["point_t"]))/ephem.second

#    print(tstr)
    
    for pi in range(len(t["point_t"])-1):
        (az0,el0)=(t["point_az"][pi],t["point_el"][pi])
        (az1,el1)=(t["point_az"][pi+1],t["point_el"][pi+1])
        tt=t["point_t"][pi]+ephem.second*dwell_time
        point_ts.append(tt)
        if debug:
            at_str="# AT \"%s\""%(ephem.Date(tt).datetime())
        else:
            at_str="AT \"%s\""%(ephem.Date(tt).datetime())
        if debug:
            # antenna starts dwell_time after pass and should be there dwell_time before target
            # hence, for testing antenna motion, we use available_time-2.0*dwell_time
            sync_str="SYNC %1.2f\nDISP -hms. \"Antenna should have stopped by now!!!\"\n%s\n"%(available_time[pi]-2.0*dwell_time,printant)
        else:
            sync_str=""

        tstr="%s\npointdirection %1.2f %1.2f\nupar 18 %1.2f\nupar 19 %1.2f\nDISP -hms. \"antenna move_time %1.2f s available_time %1.2f s\"\nDISP -hms. \"at %s satellite will be at az %1.2f el %1.2f\"\n%s"%(
            at_str,
            t["point_az"][pi+1],
            t["point_el"][pi+1],
            t["point_az"][pi+1],
            t["point_el"][pi+1],
            move_time(az0,az1,el0,el1),
            available_time[pi]-2.0*dwell_time,
            t["point_t"][pi+1],
            t["point_az"][pi+1],
            t["point_el"][pi+1],
            sync_str)

        slack.append(available_time[pi]-dwell_time-move_time(az0,az1,el0,el1))
        if (available_time[pi]-2.0*dwell_time) < move_time(az0,az1,el0,el1):
            colors.append("red")
        else:
            colors.append("green")
        track_points.append(tstr)
        print(tstr)
        azs.append(t["point_az"][pi+1])
        els.append(t["point_el"][pi+1])

    # beampark, use extra dwell time    
    tt=t["point_t"][len(t["point_t"])-1]+3*dwell_time*ephem.second
    point_ts.append(tt)
    if not debug:
        tstr="AT \"%s\"\npointdirection %1.2f %1.2f\nDISP -hms. \"back to beampark\"\nupar 17 0"%(ephem.Date(tt).datetime(),bp_az,bp_el)
    else:
        tstr="# AT \"%s\"\npointdirection %1.2f %1.2f\nDISP -hms. \"back to beampark\"\nupar 17 0\nSYNC 300\n%s\n"%(ephem.Date(tt).datetime(),bp_az,bp_el,printant)
    track_points.append(tstr)
    azs.append(bp_az)
    els.append(bp_el)

    tracklet={}
    tracklet["t0"]=t["point_t"][0]-ephem.second*setup_time
    tracklet["t1"]=ephem.Date(t["point_t"][len(t["point_t"])-1])+3*dwell_time*ephem.second
    tracklet["az"]=azs
    tracklet["el"]=els
    tracklet["track_points"] = track_points
    tracklet["colors"] = colors
    tracklet["slack"] = slack
    tracklet["point_t"] = point_ts
    tracklet["name"]=t["name"]
    tracklet["norad_id"]=t["norad_id"]
    return(tracklet)
                            

def az_el_to_xy(az,el):
    r=n.cos(n.pi*el/180.0)
    x=r*n.cos(-n.pi*az/180.0 + n.pi/2.0)
    y=r*n.sin(-n.pi*az/180.0 + n.pi/2.0)
    return((x,y))

def plan(norad_id, t0, t1, lat, lon, dwell_time=20.0, debug=False):
#    o.name=name
    
    ut0 = ephem.Date("1970/01/01 00:00:00")
    t0=ephem.Date(t0)
    t1=ephem.Date(t1)

    target=se.get_tle(norad_id)

    t=track(norad_id,
            latitude=lat,
            longitude=lon,
            startd=t0,
            endd=t1, 
            dwell_time=dwell_time)

    plt.clf()
    t["el"]=n.array(t["el"])
    t["az"]=n.array(t["az"])
    (x,y)=az_el_to_xy(t["az"],t["el"])
    plt.plot( x, y )

    (x,y)=az_el_to_xy(n.linspace(0,360,num=360),n.repeat(30.0,360))
    plt.plot( x, y ,color="black")

    (x,y)=az_el_to_xy(n.linspace(0,360,num=360),n.repeat(60.0,360))
    plt.plot( x, y ,color="black")

    (x,y)=az_el_to_xy(n.linspace(0,360,num=360),n.repeat(80.0,360))
    plt.plot( x, y ,color="black")

    # plan radar track
    tracklet=points_to_plan(t,dwell_time=dwell_time,debug=debug)

    for pi in range(12):
        (x,y)=az_el_to_xy(pi*30,0.0)
        plt.text(x,y,"%d$^{\circ}$"%(pi*30))
        #    plt.plot(x,y,".",markersize=20,color="black")

    for pi in range(len(t["point_t"])):
        (x,y)=az_el_to_xy(t["point_az"][pi],t["point_el"][pi])
        plt.text(x+0.05,y,"%s (%1.2f s)\naz %1.2f el %1.2f"%(t["point_t"][pi],tracklet["slack"][pi],t["point_az"][pi],t["point_el"][pi]),size="smaller")
        if pi == 0:
            marker="*"
        else:
            marker="."
        plt.plot(x,y,marker,markersize=20,color=tracklet["colors"][pi])
    plt.axis('off')
    plt.xlim([-1.1,1.1])
    plt.ylim([-1.1,1.1])
    plt.axes().set_aspect('equal', 'datalim')
    plt.title("%s %s-%s"%(target["name"],t0,t1))
    #plt.plot(t["hv"],t["el"])
    utsec=(t0-ut0)/ephem.second
    plt.savefig("plots/pass-%s.png"%(utsec))
    return(tracklet)
#    plt.show()

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-n", "--name", dest="name",
                      help="Satellite name")
    
    parser.add_option("-0", "--t0", dest="t0", default="2016/01/01 00:00:00",
                      help="Start of track")
    
    parser.add_option("-1", "--t1", dest="t1", default="2016/01/01 00:00:00",
                      help="End of track")
    
    parser.add_option("-a", "--lat", dest="lat", default="69:35:11.0",
                      help="Latitude")
    
    parser.add_option("-b", "--lon", dest="lon", default="19:13:38.0",
                      help="Longitude")
    
    (o, args) = parser.parse_args()
    plan(o.name,o.t0,o.t1,o.lat,o.lon)
    
