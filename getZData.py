import sys
from datetime import datetime
import time
from pyzabbix import ZabbixAPI
from datetime import timedelta
from pymongo import Connection
from datetime import timedelta
from pymongo.errors import ConnectionFailure

def zapi():
	zapi = ZabbixAPI("")
	zapi.login("", "")
	return zapi

def mongoclient(host,port,dbname):
	''' host: mongodb hostname
	port: mongodb port
	dbname: mongodb database names
	times: times before now to get logs from mongodb,eg:-10
	'''
	try:
		_c1 = Connection(host, port)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		sys.exit(1)
	dbC = _c1[dbname]
	assert dbC.connection == _c1
	return dbC
	
def badip2mongo(dbC,collect,iplist):
	for ip in iplist:
		if ip[0] in comiplist.comiplist():
			continue
		i = dbC[collect].find_one({"ip":ip[0]})
		if i:
			c1 = i.get("counts") + 1
			dbC[collect].update({"ip":ip[0]},{"$set":{"counts":c1}}, save=True)
		else:
			dbC[collect].insert({"ip":ip[0],"counts":1}, save=True)


def gItemid(idlist,itemkey):
	item1 = {}
	for id in idlist:
		for h in zapi().item.get(hostids=id,search={"key_":itemkey}):
			i = h['itemid']
			item1[i] = id
	
	return item1

def time1():
	timeA = []
	for i in xrange(-2,0):
		t1 = datetime(2013,10,14,23,59,59)
		t2 = timedelta(days=i)
		t = t1 + t2
		time_till = time.mktime(t.timetuple())
		timeA.append(time_till)
	return timeA


def gHistory(itemlist,timeS):
	value1 = []
	valuedays = {}
	for i in itemlist:
		for j in timeS:
			if len(value1):
				del value1[:]
			
			# Create a time range
			item_id = i
			time_till = j
			time_from = time_till - 60 * 60 * 24  # 24 hours
		
			# Query item's trend data
			history = zapi().history.get(itemids=[item_id],
				time_from=time_from,
				time_till=time_till,
				output='extend',
				limit='2000',
			)
		
			# If nothing was found, try getting it from history
			if not len(history):
				history = zapi().history.get(itemids=[item_id],
					time_from=time_from,
					time_till=time_till,
					output='extend',
					limit='2000',
					history=0,
				)
			for point in history:
				value1.append(int(point['value']))
			m1 = max(value1)
			valuedays[datetime.fromtimestamp(j)] = m1
			
	
	print valuedays
				#print("{0}: {1}".format(datetime.fromtimestamp(int(point['clock'])).strftime("%x %X"), point['value']))
	
if __name__=="__main__":
	a = [u'10141']
	k = u"net.if.in"
	t = time1()
	l = gItemid(a,k)
	gHistory(l,t)
