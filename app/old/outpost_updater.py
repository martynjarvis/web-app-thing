# -*- coding: utf-8 -*-

import datetime
import pymysql 

from lib.eveapi import EVEAPIConnection
from lib.eveapi import Error as api_error

def get_db():
    return pymysql.connect(host="localhost",port=3306,user="test",passwd="pleaseignore",db="wallet")

def fetch_all():        
    print 'Updating all from eve api.'
    db = get_db()
    cur = db.cursor()
    
    con = EVEAPIConnection()
    try:
        outpost_list = con.eve.ConquerableStationList()
    except api_error, e:
        print "eveapi returned the following error:"
        print "code:", e.code
        print "message:", e.message
        return
    except Exception, e:
        print "Something went horribly wrong:" + str(e)
        return
    #print outpost_list
    for outpost in outpost_list.outposts:
        print outpost.stationName
        cur.execute(''' insert into outpost(stationID,stationName, stationTypeID, solarSystemID, corporationID, corporationName)
                values(%s,%s,%s,%s,%s,%s)''', 
                (outpost.stationID, outpost.stationName, outpost.stationTypeID, outpost.solarSystemID, outpost.corporationID, outpost.corporationName) )
 
    db.commit() 
    db.close() 
    
if __name__ == '__main__':
    fetch_all()
