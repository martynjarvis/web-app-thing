# -*- coding: utf-8 -*-

import pymysql 
import getpass

def get_db():
    password=getpass.getpass('Password for root?')
    return pymysql.connect(host="localhost",port=3306,user="root",passwd=password,db="wallet")

def correct_all(correction_list):
    db = get_db()
    cur = db.cursor()
    for correction in correction_list : 
        print "Setting group %s (%s) to volume %s" % (correction[2],correction[0],correction[1])
        cur.execute("UPDATE eve.invtypes SET volume=%s WHERE groupID=%s",
                      [correction[1],correction[0]])
    db.commit()
    db.close()
    print "Done."

if __name__ == '__main__':
    correction_list = (
        (324,2500,"AssaultShip"),
        (419,15000,"Combat Battlecruiser"),
        (1201,15000,"Attack Battlecruiser"),
        (27,50000,"Battleship"),
        (898,50000,"BlackOps"),
        (883,1000000,"CapitalIndustrialShip"),
        (29,500,"Capsule"),
        (547,1000000,"Carrier"),
        (906,10000,"CombatReconShip"),
        (540,15000,"CommandShip"),
        (830,2500,"CovertOps"),
        (26,10000,"Cruiser"),
        (420,5000,"Destroyer"),
        (485,1000000,"Dreadnought"),
        (893,2500,"ElectronicAttackShips"),
        (381,50000,"EliteBattleship"),
        (543,3750,"Exhumer"),
        (833,10000,"ForceReconShip"),
        (513,1000000,"Freighter"),
        (25,2500,"Frigate"),
        (358,10000,"HeavyAssaultShip"),
        (894,10000,"HeavyInterdictors"),
        (28,20000,"Industrial"),
        (941,500000,"IndustrialCommandShip"),
        (831,2500,"Interceptor"),
        (541,5000,"Interdictor"),
        (902,1000000,"JumpFreighter"),
        (832,10000,"Logistics"),
        (900,50000,"Marauders"),
        (463,3750,"MiningBarge"),
        (1022,500,"Zephyr"),
        (237,2500,"Rookieship"),
        (31,500,"Shuttle"),
        (834,2500,"StealthBomber"),
        (963,5000,"StrategicCruiser"),
        (659,1000000,"SuperCarrier"),
        (30,10000000,"Titan"),
        (380,20000,"TransportShip")
        )                  
    correct_all(correction_list)
                           

