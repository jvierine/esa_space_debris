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

def get_tle(num):
    if not os.path.exists("cache"):
        os.system("mkdir -p cache")
    if not os.path.exists("identity"):
        print("No identity file found")
        print("")
        print("Please create ascii named ""identity"" file containing: identity=username&password=password")
        print("This is your space-track.org username and password.")
    identity=file("identity","r").read().strip()
    print(identity)
    
    if not os.path.exists("cache/%s"%(num)):
        print("Fetching %s"%(num))
        os.system("wget  --post-data='%s&query=https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/NORAD_CAT_ID/38086/orderby/TLE_LINE1 ASC/format/3le' --cookies=on --keep-session-cookies --save-cookies=cookies.txt 'https://www.space-track.org/ajaxauth/login' -O cache/%s"%(identity,num))

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
    print(tle)

# envisat={"name":"ENVISAT",
#          "tle1":"1 27386U 02009A   16223.12388893  .00000012  00000-0  17853-4 0  9994",
#          "tle2":"2 27386  98.2782 274.5989 0001231  83.2442 276.8889 14.37872832756379"}

# ers2={"name":"ERS-2",
#       "tle1":"1 23560U 95021A   16222.47420912  .00002156  00000-0  10618-3 0  9998",
#       "tle2":"2 23560  98.5161 167.9675 0002411 292.0490  68.0485 15.19315369128031"}

# ers1={"name":"ERS-1",
#       "tle1":"1 21574U 91050A   16222.93115111  .00000100  00000-0  47373-4 0  9998",
#       "tle2":"2 21574  98.4176 169.7617 0033259 162.7915 197.4408 14.37508844312874"}

# proba1={"name":"PROBA-1",
#         "tle1":"1 26958U 01049B   16223.16256629  .00000911  00000-0  84812-4 0  9993",
#         "tle2":"2 26958  97.5180 196.0382 0072424 291.7285  67.6232 14.94807285805056"}

# swarmc={"name":"SWARM C",
#         "tle1":"1 39453U 13067C   16223.18095358  .00001815  00000-0  42956-4 0  9999",
#         "tle2":"2 39453  87.3480 285.0923 0003716  96.6105 263.5574 15.41021892152181"}

# avum_adapt={"name":"AVUM Adaptor",
#             "tle1":"1 39162U 13021D   16219.92123480 +.00000241 +00000-0 +74928-4 0  9997",
#             "tle2":"2 39162 098.7655 349.2706 0097420 087.2309 274.0028 14.47458251171648"}

# vega_avum={"name":"VEGA AVUM R/B",
#            "tle1":"1 38086U 12006K   16221.18765179  .00076477  60391-5  16725-3 0  9999",
#            "tle2":"2 38086  69.4601  84.2674 0161209 286.4276  71.9253 15.79243749241520"}

# targets=[ers1,ers2,envisat,proba1,swarmc,vega_avum,avum_adapt]
# elements={}
# for t in targets:
#     elements[t["name"]]=t

