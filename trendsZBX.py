import sys
from datetime import datetime
import time
from pyzabbix import ZabbixAPI
from datetime import timedelta
from pymongo import Connection
from datetime import timedelta
from pymongo.errors import ConnectionFailure

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
		dbC[collect].insert({"ip":ip[0],"counts":1}, save=True)

def zapi():

	zapi = ZabbixAPI("")
	zapi.login("", "")
	return zapi
	
def gHostid():
	hostid1 = {}
	for h in zapi().host.get(output='extend'):
		i = h['hostid']
		j = h['name']
		hostid1[i] = j
		
	return hostid1

def gItemid(HostidL,temkey):
	item1 = {}
	for Hostid in HostidL:
		for h in zapi().item.get(hostids=Hostid,search={"key_":itemkey}):
			i = h['itemid']
			j = h['key_']
			item1[i] = [HostidL[Hostid],j]
	
	return item1

def time1():
	timeA = []
	for i in xrange(-90,0):
		t1 = datetime(2013,10,15,22,59,59)
		t2 = timedelta(days=i)
		t = t1 + t2
		time_till = time.mktime(t.timetuple())
		timeA.append(time_till)
	return timeA


def gTrends(itemlist,timeS):
	value1 = []
	valuedays = []
	valueavg = {}
	valueall = {}
	for i in itemlist:
		if len(valuedays):
			del valuedays[:]
			
		for j in timeS:
			if len(value1):
				del value1[:]
			
			# Create a time range
			item_id = i
			time_till = j
			time_from = time_till - 60 * 60 * 14 # 14 hours
		
			# Query item's trend data
			history = zapi().trends.get(itemids=[item_id],
				time_from=time_from,
				time_till=time_till,
				output='extend',
				#limit='2000',
			)
		
			for point in history:
				value1.append(int(point['value_avg']))
			avg1 = sum(value1) / 14
			valuedays.append(avg1)
		avg = sum(valuedays)/len(valuedays)
		valueavg[(i,itemlist[i][0]),itemlist[i][1])] = avg
		
	#return valueavg
	print valueavg
	
if __name__=="__main__":
	#h = gHostid()
	h = {u'10141':'nginx111'}
	t = time1()
	for a in h:
		k = u"net.if"
		l = gItemid(a,k)
		gTrends(l,t)