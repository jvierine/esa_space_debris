#!/usr/bin/env python
#
# get tle from the space-track.org
#
# you need to supply your password and username in a file called identity.
#
# (2016) Juha Vierinen
# 
import os
from optparse import OptionParser
import json

def clear_cache():
    if os.path.exists("cache"):
        os.system("rm cache/*")

def get_cospar(norad_id):
    if not os.path.exists("cache/cospar-%s"%(norad_id)):
        identity=file("identity","r").read().strip()
    
        os.system("wget  --post-data='%s&query=https://www.space-track.org/basicspacedata/query/class/satcat/NORAD_CAT_ID/%s/orderby/INTLDES asc/metadata/true' --cookies=on --keep-session-cookies --save-cookies=cookies.txt 'https://www.space-track.org/ajaxauth/login' -O cache/cospar-%s"%(identity,norad_id,norad_id))

    with open("cache/cospar-%s"%(norad_id)) as d:
        data = json.load(d)

    return(data["data"][0]["OBJECT_ID"])
        
    
def get_tle(num):
    if not os.path.exists("cache"):
        os.system("mkdir -p cache")
    if not os.path.exists("identity"):
        print("No identity file found")
        print("")
        print("Please create ascii named ""identity"" file containing: identity=username&password=password")
        print("This is your space-track.org username and password.")
    identity=file("identity","r").read().strip()
    
    if not os.path.exists("cache/%s"%(num)):
        print("Fetching %s"%(num))
        os.system("wget  --post-data='%s&query=https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/NORAD_CAT_ID/%s/orderby/TLE_LINE1 ASC/format/3le' --cookies=on --keep-session-cookies --save-cookies=cookies.txt 'https://www.space-track.org/ajaxauth/login' -O cache/%s"%(identity,num,num))

    l=file("cache/%s"%(num),"r")
    l0=l.readline().strip()
    name=l0[2:len(l0)]
    l1=l.readline().strip()
    l2=l.readline().strip()
    return({"name":name,"tle1":l1,"tle2":l2})

if __name__ == "__main__":
    parser = OptionParser()
    
    parser.add_option("-n", "--number", dest="number", default="27386", type="string",
                      help="NORAD ID number")
    (o, args) = parser.parse_args()
    tle=get_tle(o.number)
    c=get_cospar(o.number)
    print(tle)

