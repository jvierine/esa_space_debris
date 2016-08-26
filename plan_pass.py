#!/usr/bin/env python

import ephem, sys, math
import os, errno, time 
import matplotlib.pyplot as plt
import numpy as n
from optparse import OptionParser
import sat_elements as se

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

parser.add_option("-p", "--n_pos", dest="n_pos", default=4,
                  help="Number of pointing positions.")

(o, args) = parser.parse_args()

if not se.elements.has_key(o.name):
    print("Satellite %s not found"%(o.name))
    exit(0)

ut0 = ephem.Date("1970/01/01 00:00:00")

def track(target,
          startd = ephem.Date("2016/09/01 00:00:00"),
          endd = ephem.Date("2016/09/01 00:00:00"),
          latitude="69:35:11.0",
          longitude="19:13:38.0",
          altitude=86.0,
          n_points=4):

    obs = ephem.Observer()
    obs.lat = latitude
    obs.long = longitude
    obs.elevation = altitude
    dt_sec = int((endd-startd)/ephem.second)
    spacing=float(dt_sec)/float(n_points)
    print("time between positions %1.2f s"%(spacing))

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
    for i in range(0,int(dt_sec),1):
        #    obs.date = 
        obs.date = startd + float(i)*ephem.second
        sat.compute(obs)
        el = 360.0*float(sat.alt)/2.0/math.pi
#        az = 360.0*float(-sat.az)/2.0/math.pi + 90
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
        if el > maxel:
            maxel=el
            maxaz=az
            maxelt=obs.date
            maxr=r

    point_t=[]
    point_az=[]
    point_el=[]
    for i in range(0,int(dt_sec),int(spacing)):
        obs.date = startd + float(i)*ephem.second
        sat.compute(obs)
        el = 360.0*float(sat.alt)/2.0/math.pi
        az = 360.0*float(sat.az)/2.0/math.pi 
        r = float(sat.range)
        alt = float(sat.elevation)
        vel = float(sat.range_velocity)
        sublat = 360.0*float(sat.sublat)/2.0/math.pi
        sublong = 360.0*float(sat.sublong)/2.0/math.pi
        point_t.append(obs.date)
        point_az.append(az)
        point_el.append(el)
#        print("pointdir %1.2f %1.2f"%(az,el))
    point_az=n.array(point_az)
    point_el=n.array(point_el)
    return({"hv":hv,"az":azv,"el":elv,"name":target["name"],"peakel":maxel,"point_t":point_t,"point_az":point_az,"point_el":point_el,"dt":spacing})


def move_time(az0,az1,el0,el1,az_speed=2.0,el_speed=2.0):
    dang=n.abs(180.0*n.angle((n.exp(1j*n.pi*az1/180.0)/n.exp(1j*n.pi*az0/180.0)))/n.pi)
    return(n.max([dang/az_speed,n.abs(el1-el0)/el_speed]))

# dwell_time is move antenna n sec after target has passed the point
def points_to_plan(t,setup_time=5*60,dwell_time=10):
    print("Dwell %1.2f s, setup %1.2f s"%(dwell_time,setup_time))
    print("at %s go to %1.2f %1.2f"%(ephem.Date(t["point_t"][0]-ephem.second*setup_time),t["point_az"][0],t["point_el"][0]))
    for pi in range(len(t["point_t"])-1):
        (az0,el0)=(t["point_az"][pi],t["point_el"][pi])
        (az1,el1)=(t["point_az"][pi+1],t["point_el"][pi+1])
        print("at %s go to %1.2f %1.2f antenna move_time %1.2f available_time %1.2f"%(ephem.Date(t["point_t"][pi]+ephem.second*dwell_time),t["point_az"][pi+1],t["point_el"][pi+1],move_time(az0,az1,el0,el1),t["dt"]-dwell_time))

t0=ephem.Date(o.t0)
t1=ephem.Date(o.t1)

print(t0)
print(t1)

t=track(target=se.elements[o.name],
        latitude=o.lat,
        longitude=o.lon,
        startd=t0,
        endd=t1, 
        n_points=o.n_pos)

def az_el_to_xy(az,el):
    r=n.cos(n.pi*el/180.0)
    x=r*n.cos(-n.pi*az/180.0 + n.pi/2.0)
    y=r*n.sin(-n.pi*az/180.0 + n.pi/2.0)
    return((x,y))
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

points_to_plan(t)

for pi in range(12):
    (x,y)=az_el_to_xy(pi*30,0.0)
    plt.text(x,y,"%d$^{\circ}$"%(pi*30))
#    plt.plot(x,y,".",markersize=20,color="black")

for pi in range(len(t["point_t"])):
    (x,y)=az_el_to_xy(t["point_az"][pi],t["point_el"][pi])
    plt.text(x+0.05,y,t["point_t"][pi])
    plt.plot(x,y,".",markersize=20,color="black")
plt.axis('off')
plt.xlim([-1.1,1.1])
plt.ylim([-1.1,1.1])
plt.title("%s %s-%s"%(o.name,o.t0,o.t1))
#plt.plot(t["hv"],t["el"])
utsec=(t0-ut0)/ephem.second
plt.savefig("pass-%s.png"%(utsec))
plt.show()
