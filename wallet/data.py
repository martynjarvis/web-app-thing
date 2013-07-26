from wallet import app

import datetime
import urllib2
import xml.etree.ElementTree as etree 

# use this for ajax calls etc

# @app.route('/data/history')
# def data_history():
    # ''' get history data from eve market data '''
    # # url ="http://api.eve-marketdata.com/api/item_history2.xml?char_name=scruff_decima&days=30&region_ids=10000002&type_ids=34"
    # # try: 
        # # response = urllib2.urlopen(url)
    # # except Exception, e:
        # # print "Error retieving url : " + str(url) + "\n" + str(e)
        # # return
    # retVal = [
    # "2013-06-27,	5.08 " ,
    # "2013-06-28,	5.05 " ,
    # "2013-06-29,	5.05 " ,
    # "2013-06-30,	5.05 " ,
    # "2013-07-01,	5.01 " ,
    # "2013-07-02,	5.05 " ,
    # "2013-07-03,	5.05 " ,
    # "2013-07-04,	5.05 " ,
    # "2013-07-05,	5.08 " ,
    # "2013-07-06,	5.08 " ,
    # "2013-07-07,	5.05 " ,
    # "2013-07-08,	5.05 " ,
    # "2013-07-09,	5.08 " ,
    # "2013-07-10,	5.03 " ,
    # "2013-07-11,	5.07 " ,
    # "2013-07-12,	5.01 " ,
    # "2013-07-13,	4.99 " ,
    # "2013-07-14,	4.92 " ,
    # "2013-07-15,	4.96 " ,
    # "2013-07-16,	4.95 " ,
    # "2013-07-17,	4.9	 " ,
    # "2013-07-18,	4.94 " ,
    # "2013-07-19,	4.87 " ,
    # "2013-07-20,	4.9	 " ,
    # "2013-07-21,	4.88 " ,
    # "2013-07-22,	4.83 " ,
    # "2013-07-23,	4.84 " ,
    # "2013-07-24,	4.88 " ,
    # "2013-07-25,	4.87 " ,
    # "2013-07-26,	3.22 " ]

        
    # # retVal = []
    # # tree = etree.parse(response)
    # # rowset = tree.getroot().find("result").find("rowset")
    # # if rowset.getchildren() :
        # # for row in rowset :
            # # retVal.append( ','.join([str(row.get("date")),str(row.get("avgPrice"))]) )
    # return '\n'.join(retVal)

