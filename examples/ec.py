#!/usr/bin/env python
from __future__ import print_function

import cobra.eventchannel
import cobra.mit.session
import cobra.mit.access
import cobra.mit.request
import cobra.mit.mo
import cobra.model.fv
import cobra.model.pol
import threading
import random
import string
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

apicuri = 'https://apic'
apicuser = 'admin'
apicpassword = 'password'

randomstring = lambda x: ''.join(
	random.choice(string.lowercase) for i in range(x))

moDirLock = threading.Lock()

class TimerThread():

	def __init__(self, wait_time, func, parm):
		print('Calling {} every {} seconds'.format(func, wait_time))
		self.wait_time = wait_time
		self.callback = func
		self.parm = parm
		self.thread = threading.Timer(self.wait_time, self.run_callback)
		self.thread.daemon = True
		self.thread.start()
	def run_callback(self):
		self.callback(self.parm)
		self.thread = threading.Timer(self.wait_time, self.run_callback)
		self.thread.start()
	def start(self):
		self.thread.start()
	def cancel(self):
		self.thread.cancel()
 
def refreshSub(sub):
	with moDirLock:
		print('Refreshing subscription')
		sub.refresh()

def reauthSess(md):
	with moDirLock:
		print('*' * 30)
		print('Reauthing Session')
		md.reauth()

def createEPGs(md):
	topMo = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(topMo, name='test')
	fvAp = cobra.model.fv.Ap(fvTenant, name='test', descr='test')
	cobra.model.fv.AEPg(fvAp, name=randomstring(32), descr=randomstring(32))
	c = cobra.mit.request.ConfigRequest()
	c.addMo(fvTenant)
	with moDirLock:
		print('Creating new EPG')
		md.commit(c)


fmt = 'xml'
mock = False

ls = cobra.mit.session.LoginSession(apicuri, apicuser, apicpassword, secure=False, requestFormat=fmt)
md = cobra.mit.access.MoDirectory(ls)
md.login()

# ls = LoginSession(...)  # this would login automatically, MoDirectory would no longer have a login() method
# ec = EventChannel(ls)  # Event channel needs a session
# moDir = MoDirectory(ls)  # MoDirectory needs a session

ec = cobra.eventchannel.EventChannel(ls)
cq = cobra.mit.request.ClassQuery('fvAEPg')
sub = ec.subscribe(cq)
print(sub.subid)

subtimer = TimerThread(55, refreshSub, sub)
sesstimer = TimerThread(ls.refreshTimeoutSeconds-10, reauthSess, md)
createtimer = TimerThread(10, createEPGs, md)

dicttable = lambda d: '\n'.join(['{:{width}}: {}'.format(k, v, width=max(map(len, d.keys()))) for k,v in sorted(d.items(), key=lambda x: x[0])])

if fmt == 'xml':
	eventStr = '''<?xml version="1.0" encoding="UTF-8"?> <imdata subscriptionId="72342148523360257"> <fvAEPg childAction="" configIssues="" configSt="applied" descr="jgnsflhmnufhqwtjkskaegmcsqcrhflg" dn="uni/tn-test/ap-test/epg-dkwruifqicziomhkztugizirtkijrzso" lcOwn="local" matchT="AtleastOne" modTs="2015-03-04T17:52:49.101+00:00" monPolDn="uni/tn-common/monepg-default" name="dkwruifqicziomhkztugizirtkijrzso" pcTag="any" prio="unspecified" rn="" scope="2686976" status="created" triggerSt="not_triggerable" uid="15374"/> <fvAEPg childAction="" configIssues="" configSt="applied" descr="jgnsflhmnufhqwtjkskaegmcsqcrhflg" dn="uni/tn-test/ap-test/epg-dkwruifqicziomhkztugizirtkijrzso" lcOwn="local" matchT="AtleastOne" modTs="2015-03-04T17:52:49.101+00:00" monPolDn="uni/tn-common/monepg-default" name="dkwruifqicziomhkztugizirtkijrzso" pcTag="any" prio="unspecified" rn="" scope="2686976" status="created" triggerSt="not_triggerable" uid="15374"/> <fvAEPg childAction="" configIssues="" configSt="applied" descr="jgnsflhmnufhqwtjkskaegmcsqcrhflg" dn="uni/tn-test/ap-test/epg-dkwruifqicziomhkztugizirtkijrzso" lcOwn="local" matchT="AtleastOne" modTs="2015-03-04T17:52:49.101+00:00" monPolDn="uni/tn-common/monepg-default" name="dkwruifqicziomhkztugizirtkijrzso" pcTag="any" prio="unspecified" rn="" scope="2686976" status="created" triggerSt="not_triggerable" uid="15374"/> </imdata> '''
else:
	eventStr = '''{"imdata": [{"fvAEPg": {"attributes": {"childAction": "", "configIssues": "", "configSt": "applied", "descr": "qpbuqqtzwrksaadklahpotcvzdiknhiz", "dn": "uni/tn-test/ap-test/epg-qllnuxkzzikqwdbihufarjcxbfczlfqs", "lcOwn": "local", "matchT": "AtleastOne", "modTs": "2015-03-04T18:52:08.870+00:00", "monPolDn": "uni/tn-common/monepg-default", "name": "qllnuxkzzikqwdbihufarjcxbfczlfqs", "pcTag": "any", "prio": "unspecified", "rn": "", "scope": "2686976", "status": "created", "triggerSt": "not_triggerable", "uid": "15374"} } }, {"fvAEPg": {"attributes": {"childAction": "", "configIssues": "", "configSt": "applied", "descr": "qpbuqqtzwrksaadklahpotcvzdiknhiz", "dn": "uni/tn-test/ap-test/epg-qllnuxkzzikqwdbihufarjcxbfczlfqs", "lcOwn": "local", "matchT": "AtleastOne", "modTs": "2015-03-04T18:52:08.870+00:00", "monPolDn": "uni/tn-common/monepg-default", "name": "qllnuxkzzikqwdbihufarjcxbfczlfqs", "pcTag": "any", "prio": "unspecified", "rn": "", "scope": "2686976", "status": "created", "triggerSt": "not_triggerable", "uid": "15374"} } } ], "subscriptionId": ["72060695021486081"] } '''

while True:

	e = ec.retrieveEvents()

	for moevent in e:


		print(dicttable({
			'Event': moevent.moEventType,
			'Dn': moevent.dn,
			'Class Name': moevent.moClassName
		}))

		if not moevent.__class__.__name__ == 'MoDelete':
			print('-' * 10)
			print(dicttable(moevent.changes))
		
		print('=' * 20)
		print('=' * 20)
		print('=' * 20)

	if mock:
		break

topMo = cobra.model.pol.Uni('')
fvTenant = cobra.model.fv.Tenant(topMo, name='test')
fvTenant.delete()
c = cobra.mit.request.ConfigRequest()
c.addMo(fvTenant)
md.commit(c)

