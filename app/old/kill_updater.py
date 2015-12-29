# -*- coding: utf-8 -*-

import time
import datetime
import urllib2
import pymysql 
import json
from StringIO import StringIO
import gzip

def get_db():
    return pymysql.connect(host="localhost",port=3306,user="test",passwd="pleaseignore",db="wallet")

def fetch_kills():        
    print 'Updating Kills.'

    db = get_db()
    cur = db.cursor() 
    
    # most recent kill in db
    cur.execute('''select max(killID) from zk_kill;''')
    last_id = cur.fetchall()[0][0]
    
    # fetch kills since most recent, max 7 days back
    #url ="https://zkillboard.com/api/losses/no-attackers/api-only/pastSeconds/604800/allianceID/498125261/"
    # url ="https://zkillboard.com/api/losses/no-attackers/api-only/pastSeconds/604800/allianceID/498125261/afterKillID/%s/" % last_id
    #url ="https://zkillboard.com/api/losses/no-attackers/api-only/allianceID/498125261/afterKillID/%s/" % last_id
    
    url ="https://zkb.pleaseignore.com/api/losses/no-attackers/api-only/allianceID/498125261/afterKillID/%s/" % last_id
    
    page = 1
    count = 0
    
    while True:
        print "Page %s" % str(page)
        #print url + "page/%s/" % str(page)
        try: 
            request = urllib2.Request(url + "page/%s/" % str(page), headers={"Accept-Encoding":"gzip","User-Agent":"ScruffDecima"})
            response = urllib2.urlopen(request)
        except Exception, e:
            print "Error retieving url : " + str(url) + "\n" + str(e)
            return
            
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            data = response.read() 
            
        kills = json.loads(data)
        
        for kill in kills:
            try: 
                cur.execute('''
                    INSERT INTO zk_kill (killID ,solarSystemID,killTime,victimID,shipTypeID) 
                    VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE killID=killID''' ,
                    (kill["killID"],kill["solarSystemID"],kill["killTime"],
                     kill["victim"]["characterID"],kill["victim"]["shipTypeID"]))
            except Exception, e:
                print "Error adding killID %s \n %s" % (str(kill["killID"]), str(e) )
                continue
            
            for loot in kill["items"] :
                try: 
                    cur.execute('''
                    INSERT INTO zk_loot (killID,typeID,flag,qtyDropped,qtyDestroyed) 
                    VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE killID=killID''' ,
                    (kill["killID"],loot["typeID"],loot["flag"],
                    loot["qtyDropped"],loot["qtyDestroyed"]))
                except Exception, e:
                    print "Error adding typeID %s to killID %s \n %s" % (str(loot["typeID"]) , str(kill["killID"]), str(e) )
                    continue
            count+=1
        
        if len(kills) < 200: break # max 200 per page, break if incomplete page
        page+=1
        time.sleep(10) # by request of zkb(might be able to bring this down)
        
    db.commit()
    db.close()
    print 'Updating Kills. - DONE'
    print '%s kills added to db.' % count
        
if __name__ == '__main__':
    fetch_kills()
