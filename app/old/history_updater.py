# -*- coding: utf-8 -*-

import time
import urllib2
import xml.etree.ElementTree as etree 
import pymysql 

def get_db():
    return pymysql.connect(host="localhost",port=3306,user="test",passwd="pleaseignore",db="wallet")

def chunks(l, n):
  for i in range(0, len(l), n):
    yield l[i:i+n]


def fetch_market_hist():        
    print 'Updating market hist.'

    db = get_db()
    cur = db.cursor()

    cur.execute("""SELECT typeID FROM eve.invtypes 
                   WHERE marketGroupID IS NOT NULL""")
    
    region_ids = [10000002,10000048] # forge, placid
    emd_base_url ="http://api.eve-marketdata.com/api/item_history2.xml?char_name=scruff_decima&days=60&region_ids="

    
    for region_id in region_ids :
        emd_base_url = emd_base_url + str(region_id) + "," 
    emd_base_url = emd_base_url[:-1] # remove last comma

    type_ids = cur.fetchall()
    type_ids = chunks(type_ids,25)
    for type_id_chunk in type_ids :
        url=emd_base_url+"&type_ids="
        for x in type_id_chunk :
            url+=str(x[0])+","
        url = url[:-1] # remove last comma
        print url
        try: 
            response = urllib2.urlopen(url)
        except Exception, e:
            print "Error retieving url : " + str(url) + "\n" + str(e)
            continue
        tree = etree.parse(response)
        rowset = tree.getroot().find("result").find("rowset")
        if rowset.getchildren() :
            for row in rowset :
                cur.execute(""" INSERT INTO market_hist (type_id, region_id, date,
                low_price, high_price, avg_price, volume, orders) 
                VALUES ( %s,%s,%s,%s,%s,%s,%s,%s) 
                ON DUPLICATE KEY UPDATE
                low_price=%s,
                high_price=%s,
                avg_price=%s,
                volume=%s,
                orders=%s """,
                [row.get("typeID"), 
                  row.get("regionID"),
                  row.get("date"),
                  row.get("lowPrice"),
                  row.get("highPrice"),
                  row.get("avgPrice"),
                  row.get("volume"),
                  row.get("orders"),
                  row.get("lowPrice"),
                  row.get("highPrice"),
                  row.get("avgPrice"),
                  row.get("volume"),
                  row.get("orders")])
        time.sleep(0.5)


    db.commit()
    db.close()
    print 'Updating market hist. - DONE'

if __name__ == '__main__':
    fetch_market_hist()
