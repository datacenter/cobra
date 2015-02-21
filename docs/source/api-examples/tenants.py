# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python


# Import access classes
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ConfigRequest

# Import model classes
from cobra.model.fvns import VlanInstP, EncapBlk
from cobra.model.infra import RsVlanNs
from cobra.model.fv import Tenant, Ctx, BD, RsCtx, Ap, AEPg, RsBd, RsDomAtt
from cobra.model.vmm import DomP, UsrAccP, CtrlrP, RsAcc


# Policy information
VMM_DOMAIN_INFO = {'name': "mininet",
                   'ctrlrs': [{'name': 'vcenter1', 'ip': '192.0.20.3', 
                               'scope': 'vm'}],
                   'usrs': [{'name': 'admin', 'usr': 'administrator',
                             'pwd': 'pa$$word1'}],
                   'namespace': {'name': 'VlanRange', 'from': 'vlan-100',
                                 'to': 'vlan-200'}
                  }

TENANT_INFO = [{'name': 'ExampleCorp',
                'pvn': 'pvn1',
                'bd': 'bd1',
                'ap': [{'name': 'OnlineStore',
                        'epgs': [{'name': 'app'},
                                 {'name': 'web'},
                                 {'name': 'db'},
                                ]
                       },
                      ]
                }
              ]

def main(host, port, user, password):

    # CONNECT TO APIC
    print('Initializing connection to APIC...')
    apicUrl = 'http://%s:%d' % (host, port)
    moDir = MoDirectory(LoginSession(apicUrl, user, password))
    moDir.login()

    # Get the top level Policy Universe Directory
    uniMo = moDir.lookupByDn('uni')
    uniInfraMo = moDir.lookupByDn('uni/infra')

    # Create Vlan Namespace
    nsInfo = VMM_DOMAIN_INFO['namespace']
    print "Creating namespace %s.." % (nsInfo['name'])
    fvnsVlanInstPMo = VlanInstP(uniInfraMo, nsInfo['name'], 'dynamic')
    #fvnsArgs = {'from': nsInfo['from'], 'to': nsInfo['to']}
    EncapBlk(fvnsVlanInstPMo, nsInfo['from'], nsInfo['to'], name=nsInfo['name'])
    
    nsCfg = ConfigRequest()
    nsCfg.addMo(fvnsVlanInstPMo)
    moDir.commit(nsCfg)

    # Create VMM Domain
    print('Creating VMM domain...')

    vmmpVMwareProvPMo = moDir.lookupByDn('uni/vmmp-VMware')
    vmmDomPMo = DomP(vmmpVMwareProvPMo, VMM_DOMAIN_INFO['name'])
    
    vmmUsrMo = []
    for usrp in VMM_DOMAIN_INFO['usrs']:
        usrMo = UsrAccP(vmmDomPMo, usrp['name'], usr=usrp['usr'],
                        pwd=usrp['pwd'])
        vmmUsrMo.append(usrMo)

    # Create Controllers under domain
    for ctrlr in VMM_DOMAIN_INFO['ctrlrs']:
        vmmCtrlrMo = CtrlrP(vmmDomPMo, ctrlr['name'], scope=ctrlr['scope'],
                            hostOrIp=ctrlr['ip'])
        # Associate Ctrlr to UserP
        RsAcc(vmmCtrlrMo, tDn=vmmUsrMo[0].dn)
    
    # Associate Domain to Namespace
    RsVlanNs(vmmDomPMo, tDn=fvnsVlanInstPMo.dn)
   
    vmmCfg = ConfigRequest()
    vmmCfg.addMo(vmmDomPMo)
    moDir.commit(vmmCfg)
    print "VMM Domain Creation Completed."

    print "Starting Tenant Creation.."
    for tenant in TENANT_INFO:
        print "Creating tenant %s.." % (tenant['name'])
        fvTenantMo = Tenant(uniMo, tenant['name'])
        
        # Create Private Network
        Ctx(fvTenantMo, tenant['pvn'])
        
        # Create Bridge Domain
        fvBDMo = BD(fvTenantMo, name=tenant['bd'])
        
        # Create association to private network
        RsCtx(fvBDMo, tnFvCtxName=tenant['pvn'])
        
        # Create Application Profile
        for app in tenant['ap']:
            print 'Creating Application Profile: %s' % app['name']
            fvApMo = Ap(fvTenantMo, app['name'])
            
            # Create EPGs 
            for epg in app['epgs']:
                
                print "Creating EPG: %s..." % (epg['name']) 
                fvAEPgMo = AEPg(fvApMo, epg['name'])
                
                # Associate EPG to Bridge Domain 
                RsBd(fvAEPgMo, tnFvBDName=tenant['bd'])
                # Associate EPG to VMM Domain
                RsDomAtt(fvAEPgMo, vmmDomPMo.dn)

        # Commit each tenant seperately
        tenantCfg = ConfigRequest()
        tenantCfg.addMo(fvTenantMo)
        moDir.commit(tenantCfg)
    print('All done!')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser("Tenant creation script")
    parser.add_argument('-d', '--host', help='APIC host name or IP',
                        required=True)
    parser.add_argument('-e', '--port', help='server port', type=int,
                        default=80)
    parser.add_argument('-p', '--password', help='user password',
                        required=True)
    parser.add_argument('-u', '--user', help='user name', required=True)
    args = parser.parse_args()
    
    main(args.host, args.port, args.user, args.password)

