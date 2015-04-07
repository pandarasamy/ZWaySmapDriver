import time
import json
import os.path
import time
import requests as req
from twisted.python import log

from smap.driver import SmapDriver
from smap.util import periodicSequentialCall

class ZwayDriver(SmapDriver):
     def setup(self, opts):	
         self.apiurl = opts.get('apiurl')
         with open(opts.get('db'), 'r') as fp:
             self.db = json.load(fp)
         tz = opts.get('Properties/Timezone', 'Asia/Kolkata')
         for device in self.db["device"]:
             path = str('/' + device['name'] + '/' + device['sensor'])
             self.add_timeseries(path, device['unit'], data_type=device['type'], timezone=tz)
             self.rate = int(opts.get('Rate', 5))
             self.set_metadata('/', {'Instrument/SamplingPeriod' : str(self.rate),})

     def start(self):
         periodicSequentialCall(self.update).start(self.rate)

     def update(self):
		try:
			url = str(self.apiurl + "/" + str(int(time.time()-30)))
			print url
			res = req.post(url)
			res = json.loads(res.text)
			print res
			for dev in self.db["device"]:
				path = str('/' + dev['name'] + '/' + dev['sensor'])
				# devices.4.instances.0.commandClasses.50.data.2
				key = str('devices.' + str(dev['device']) + '.instances.'+ str(dev['instance']) + '.commandClasses.'+ str(dev['commandClass']) + '.data.'+ str(dev['data']))
				print path, key 
				if key in res:
					dd = res[key]
					val = dd['val']['value']
					updateTime = dd['val']['updateTime']
					self.add(path, int(updateTime), float(val))
					print path, val		
		except Exception, e:
			log.err()
