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


def fetch_market_order():       
    print 'Updating market orders.'
    
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        SELECT kills.typeID FROM
            ( SELECT zk_loot.typeID as typeID, sum(qtyDropped+qtyDestroyed)/4.0 AS vol
            FROM zk_kill
            JOIN zk_loot ON zk_kill.killID = zk_loot.killID
            WHERE zk_kill.killTime > CURDATE() - INTERVAL 30 DAY
            GROUP BY typeID
            UNION
            SELECT zk_kill.shipTypeID, count(zk_kill.shipTypeID)/4.0 AS vol
            FROM zk_kill
            WHERE zk_kill.killTime > CURDATE() - INTERVAL 30 DAY
            GROUP BY zk_kill.shipTypeID ) kills
        JOIN
            ( SELECT type_id, avg(avg_price) AS price
            FROM market_hist WHERE region_id=%s
            AND date > CURDATE() - INTERVAL 30 DAY
            GROUP BY type_id ) avg_hist
        ON kills.typeID=avg_hist.type_id
        WHERE avg_hist.price*kills.vol>5000000
        ORDER BY avg_hist.price*kills.vol DESC ''',(10000002))
    type_ids = cur.fetchall()
    type_ids = chunks(type_ids,25)   
    
    # cur.execute('''SELECT typeID FROM eve.invtypes 
                   # WHERE marketGroupID IS NOT NULL''')#TODO reduce this number down
        
    #system_ids = [30000142,30004751,30004608] # jita, k-6k16, 6vdt     
    #emd_base_url ="http://api.eve-marketdata.com/api/item_orders2.xml?char_name=scruff_decima&buysell=a&solarsystem_ids="
    
    #region_ids = [10000002,10000014,10000060,10000058]  # the forge(jita), delve(k-6k16), fountain(6vdt))
    region_ids = [10000002,10000054,10000048]  # the forge(jita),aridia, placid
    emd_base_url ="http://api.eve-marketdata.com/api/item_orders2.xml?char_name=scruff_decima&buysell=a&region_ids="
    
    
    # system_id_string=""
    # for system_id in system_ids :
        # system_id_string += str(system_id) + "," 
    # emd_base_url += system_id_string[:-1] # remove last comma     
    
    region_id_string=""
    for region_id in region_ids :
        region_id_string += str(region_id) + "," 
    emd_base_url += region_id_string[:-1] # remove last comma
    
    #"""I suggest 20 for statistics only calls, 5 for full order lists."""


    
    for type_id_chunk in type_ids :
        url=emd_base_url+"&type_ids="
        type_id_chunk_string=""
        for x in type_id_chunk :
            type_id_chunk_string +=str(x[0])+","
        url += type_id_chunk_string[:-1] # remove last comma
        print url
        try: 
            response = urllib2.urlopen(url)
        except Exception, e:
            print "Error retieving url : " + str(url) + "\n" + str(e)
            continue
            
        tree = etree.parse(response)
        rowset = tree.getroot().find("result").find("rowset")
        if rowset.getchildren() :
            # delete old orders
            #cur.execute('''DELETE FROM market_order WHERE solarsystem_id IN (%s) AND type_id IN (%s)''' % (system_id_string[:-1],type_id_chunk_string[:-1]))
            cur.execute('''DELETE FROM market_order WHERE region_id IN (%s) AND type_id IN (%s)''' % (region_id_string[:-1],type_id_chunk_string[:-1]))
            for row in rowset :
                cur.execute(''' INSERT INTO market_order(bid, type_id, id, station_id, 
                solarsystem_id, region_id, price, vol_entered, vol_remaining, min_vol, 
                order_range, issued,expires,created) 
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ''', [
                0 if row.get("buysell")=="s" else 1,
                row.get("typeID"),
                row.get("orderID"),
                row.get("stationID"),
                row.get("solarsystemID"),
                row.get("regionID"),
                row.get("price"), 
                row.get("volEntered"),
                row.get("volRemaining"),
                row.get("minVolume"),
                row.get("range"),
                row.get("issued"),
                row.get("expires"),
                row.get("created")] )
        time.sleep(0.5)

    db.commit()
    db.close()
    print 'Updating market orders. - DONE'

if __name__ == '__main__':
    fetch_market_order()
