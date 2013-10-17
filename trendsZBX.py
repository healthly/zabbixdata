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
	for h in zapi().host.get(groupids=['8','11','12','6','15'],output='extend'):
		i = h['hostid']
		j = h['name']
		hostid1[i] = j
		
	return hostid1

def gItemid(HostidL,itemkey):
	item1 = {}
	for id in HostidL:
		for h in zapi().item.get(hostids=id,search={"key_":itemkey},output='extend'):
			i = h['itemid']
			j = h['key_']
			item1[i] = [HostidL[id],j]
	
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


def gTrends(itemlist):
	value1 = []
	valuedays = []
	valueavg = {}
	for i in itemlist:
		if len(valuedays):
			del valuedays[:]
		if len(value1):
			del value1[:]
		item_id = i
		time_till = time.mktime(datetime.now().timetuple())
		time_from = time_till - 60 * 60 * 24 * 90
		history = zapi().trends.get(itemids=[item_id],
			time_from=time_from,
			time_till=time_till,
			output='extend',
			#limit='2000',
		)
		for point in history:
			value1.append(int(point['value_avg']))
		if len(value1):
			max1 = max(value1)
			valueavg[max1] = [i,itemlist[i][0],itemlist[i][1]]
		else:
			continue
		
	return valueavg

	
def gTrends1(itemlist):
	value1 = []
	valuedays = []
	valueavg = {}
	for i in itemlist:
		if len(valuedays):
			del valuedays[:]
		if len(value1):
			del value1[:]
		item_id = i
		time_till = time.mktime(datetime.now().timetuple())
		time_from = time_till - 60 * 60 * 24 * 120 # 120 days
		history = zapi().trends.get(itemids=[item_id],
			time_from=time_from,
			time_till=time_till,
			output='extend',
			#limit='5000',
			history=0,
			)
		for point in history:
			value1.append(float(point['value_avg']))
		if len(value1):
			max1 = max(value1)
			valueavg[max1] = [i,itemlist[i][0],itemlist[i][1]]
		else:
			continue
		
	return valueavg

if __name__=="__main__":
	h = gHostid()
	k = u"net.if"
	l = gItemid(h,k)
	k2 = u"system.cpu.load[all,avg5]"
	l2 = gItemid(h,k2)
	trends = gTrends(l)
	trends2 = gTrends1(l2)
	for i in trends:
		v = float(i)/1024/1024
		v = float('%0.3f' % v)
		print "host: %s,item-net: %s,netflow: %sMps" % (trends[i][1],trends[i][2],v)
	print '#####################################################################################################'
	for j in trends2:
		print "host: %s,item-load: system.cpu.loadavg5,cpuload: %s" % (trends2[j][1],j)
