import sys
from datetime import datetime
import time
from pyzabbix import ZabbixAPI
from datetime import timedelta
def zapi():
	zapi = ZabbixAPI("http://")
	zapi.login("1", "11111")
	return zapi

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
	for i in itemlist:
		for j in timeS:
			# Create a time range
			item_id = i
			time_till = j
			time_from = time_till - 60 * 60 * 24  # 24 hours
		
			# Query item's trend data
			history = zapi().history.get(itemids=[item_id],
				time_from=time_from,
				time_till=time_till,
				output='extend',
				limit='10',
			)
		
			# If nothing was found, try getting it from history
			if not len(history):
				history = zapi().history.get(itemids=[item_id],
					time_from=time_from,
					time_till=time_till,
					output='extend',
					limit='10',
					history=0,
				)
			
			#print history
		# Print out each datapoint
		for point in history:
			print point
			#print("{0}: {1}".format(datetime.fromtimestamp(int(point['clock'])).strftime("%x %X"), point['value']))
	
if __name__=="__main__":
	a = [u'10141']
	k = u"net.if.in"
	t = time1()
	l = gItemid(a,k)
	gHistory(l,t)
