# -*- coding: utf-8 -*-

import pymysql 

def get_db():
    return pymysql.connect(host="localhost",port=3306,user="test",passwd="pleaseignore",db="wallet")

# cat IDs
# Ammo = 8
# Commodity = 17 NPC seeded items I think
# Decryptors = 35
# Deployable = 22 bubbles
# Drones = 18
# Implants = 20
# Material = 4 # crafting mats
# Modules = 7
# Planetary Commodities = 43 # refined PI
# Planetary Resources = 42 # unrefined PI
# Ship = 6
# Skill = 16
# Subsystem = 32
  
def stuff(): 
    db = get_db()
    cur = db.cursor()
    
    cur.execute(''' 
    SELECT eve.invtypes.typeName, subq.typeID, subq.quant 
    FROM
        (SELECT zk_loot.typeID as typeID, sum(zk_loot.qtyDropped+zk_loot.qtyDestroyed) as quant
        FROM zk_kill 
        JOIN zk_loot ON zk_kill.killID = zk_loot.killID
        JOIN eve.mapsolarsystems ON zk_kill.SolarSystemID = eve.mapsolarsystems.SolarSystemID
        JOIN eve.invtypes ON zk_kill.shipTypeID = eve.invtypes.typeID
        WHERE eve.mapsolarsystems.security < 0.5
        AND eve.invtypes.groupID NOT IN (1022,237,31,902,28,513,380)
        GROUP BY zk_loot.typeID) as subq
    JOIN eve.invtypes ON subq.typeID = eve.invtypes.typeID
    JOIN eve.invgroups ON eve.invtypes.groupID = eve.invgroups.groupID
    WHERE eve.invgroups.categoryID IN (20)
    ORDER BY subq.quant DESC
    ''')
    f = open('implants.txt','w')
    #AND zk_loot.flag NOT IN (5,134)
    for row in cur.fetchall() :
        f.write(','.join(str(x) for x in row))
        f.write('\n')
    f.close()


def ships(): 
    db = get_db()
    cur = db.cursor()
    
    cur.execute(''' 
    SELECT eve.invtypes.typeName, eve.invtypes.typeID, count(zk_kill.shipTypeID) as quant
    FROM zk_kill 
    JOIN eve.mapsolarsystems ON zk_kill.SolarSystemID = eve.mapsolarsystems.SolarSystemID
    JOIN eve.invtypes ON zk_kill.shipTypeID = eve.invtypes.typeID
    WHERE eve.mapsolarsystems.security < 0.5
    AND eve.invtypes.groupID NOT IN (1022,237,31,902,28,513,380)
    GROUP BY zk_kill.shipTypeID
    ORDER BY quant DESC
    ''')
    f = open('ships.txt','w')
    for row in cur.fetchall() :
        #print row
        f.write(','.join(str(x) for x in row))
        f.write('\n')
    f.close()       
    
if __name__ == '__main__':
    ships()
