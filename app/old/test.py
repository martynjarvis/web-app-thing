test = {
  "resultType" : "orders",
  "version" : "0.1",
  "uploadKeys" : [
    { "name" : "emk", "key" : "abc" },
    { "name" : "ec" , "key" : "def" }
  ],
  "generator" : { "name" : "Yapeal", "version" : "11.335.1737" },
  "currentTime" : "2011-10-22T15:46:00+00:00",
  "columns" : ["price","volRemaining","range","orderID","volEntered","minVolume","bid","issueDate","duration","stationID","solarSystemID"],
  "rowsets" : [
    {
      "generatedAt" : "2011-10-22T15:43:00+00:00",
      "regionID" : 10000065,
      "typeID" : 11134,
      "rows" : [
        [8999,1,32767,2363806077,1,1,False,"2011-12-03T08:10:59+00:00",90,60008692,30005038],
        [11499.99,10,32767,2363915657,10,1,False,"2011-12-03T10:53:26+00:00",90,60006970,None],
        [11500,48,32767,2363413004,50,1,False,"2011-12-02T22:44:01+00:00",90,60006967,30005039]
      ]
    },
    {
      "generatedAt" : "2011-10-22T15:42:00+00:00",
      "regionID" : None,
      "typeID" : 11135,
      "rows" : [
        [8999,1,32767,2363806077,1,1,False,"2011-12-03T08:10:59+00:00",90,60008692,30005038],
        [11499.99,10,32767,2363915657,10,1,False,"2011-12-03T10:53:26+00:00",90,60006970,None],
        [11500,48,32767,2363413004,50,1,False,"2011-12-02T22:44:01+00:00",90,60006967,30005039]
      ]
    },
    {
      "generatedAt" : "2011-10-22T15:43:00+00:00",
      "regionID" : 10000065,
      "typeID" : 11136,
      "rows" : []
    }
  ]
}

if test["resultType"] == "orders" : print "order!"

for row in test["rowsets"] :
    print row["typeID"]
    for order in row["rows"] :
        print order[0]