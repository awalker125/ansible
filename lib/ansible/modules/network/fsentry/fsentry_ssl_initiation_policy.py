#!/usr/bin/python
#
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import os
import tempfile
from ansible.plugins.callback import default


__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: fsentry_ssl_initiation_policy
version_added: "2.4"
short_description: Manage forum sentry SslInitiationPolicy(s).
description:
    - Create or delete a SslInitiationPolicy.
    - SslInitiationPolicy cannot be modified via the api and must be removed and recreated
options:
    ignore_hostname_verification:
        description:
            - Should we verify the hostname matches the subject when initiating a connection.
        type: bool
    description:
        description:
            - The description of the object in forum
        type: str
    signer_group:
        description:
            - The signer group to use
        type: str
        default: "DEFAULT"
    key_pair:
        description:
            - The key pair to use
        type: str
        default: yes        
    enabled_protocols:
        description:
            - Version of TLS/SSL to enable e.g 'TLSv1.2', 'TLSv1.1', 'TLSv1', 'SSLv3', 'SSLv2Hello'
        type: list
        default:
            - 'TLSv1.2'
                       
extends_documentation_fragment:
    - fsentry_base
    - fsentry_nofsg

author:
    - "Andrew Walker (@awalker125)"
    - "Andrew Partis (@partis)"
    - "Carl Stuart (@automation1002)"
notes:
    - SslInitiationPolicy cannot be modified via the api and must be removed and recreated using I(state=absent) and I(state=present)
'''

EXAMPLES = '''

#create

fsentry_ssl_initiation_policy:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: present
  description: "hello_world world"
  ignore_hostname_verification: False
  enabled_protocols:
    - "TLSv1.2"
     

#remove

fsentry_ssl_initiation_policy:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: absent

#update

#first remove
fsentry_ssl_initiation_policy:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: absent

#then create
fsentry_ssl_initiation_policy:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: present
  description: "hello_world world"
  ignore_hostname_verification: False
  enabled_protocols:
    - "TLSv1.1"

      
'''

RETURN = '''
state:
  description: current state of the SslInitiationPolicy.
  returned: on success
  type: complex
  contains:
      status:
          description: the status of the operation
          returned: when I(state=absent)
          type: str
          sample:
              - deleted
      name:
          description: ""
          returned: when state present
          type: str
      signer_group:
          description: ""
          returned: when state is present
          type: str
          samples:
            - "DEFAULT"
      enabled_protocols:
          description: ""
          returned: when state is present
          type: list
          samples:
            - "TLSv1.2"
            - "TLSv1.1"      
      ignore_hostname_verification:
          description: ""
          returned: when state is present
          type: bool
      description:
          description: ""
          returned: when state is present
          type: str 
'''  # NOQA

from ansible.module_utils.network.fsentry.common import FSentryModuleBase

try:
    from forumsentry_api.models.ssl_initiation_policy import SslInitiationPolicy
except ImportError:
    # This is handled in azure_rm_common
    pass

class FSentrySslInitiationPolicy(FSentryModuleBase):


    def __init__(self):

        # Additional args for this module
        self.module_arg_spec = dict(

            ignore_hostname_verification=dict(type='bool', default=False),
            description=dict(type='str'),
            signer_group=dict(type='str', default="DEFAULT"),
            key_pair=dict(type='str'),
            enabled_protocols=dict(dict(type='list'), default=list('TLSv1.2')),
            )


        self.module_required_if = [
            [ 'state' , 'present' , [ 'name' ] ],
            [ 'state' , 'absent' , [ 'name' ] ],
        ]


        self.results = dict(
            changed=False,
            state=dict()
        )

        # additional props for this module
        # These will have there values set as part of super().__init__
        self.ignore_hostname_verification = None
        self.description = None
        self.signer_group = None
        self.key_pair = None
        self.enabled_protocols = None        

          
                
        super(FSentrySslInitiationPolicy, self).__init__(self.module_arg_spec,
                                            supports_check_mode=True,
                                            required_if=self.module_required_if,
                                            add_file_common_args=False,
                                            fsg=False
                                            )



    def exec_module(self, **kwargs):

        want_state = SslInitiationPolicy(name=self.name,

                                        ignore_hostname_verification=self.ignore_hostname_verification,
                                        description=self.description,
                                        signer_group=self.signer_group,
                                        key_pair=self.key_pair,
                                        enabled_protocols=self.enabled_protocols
                                        
                                        )
                                        
                                        
                                        
        have_state = None
        updated_state = None
   
        api = self.ssl_initiation_policy_api
        results = dict()
        changed = False

        
        
        # Get the current state
        try:
            have_state = api.get(self.name)
        except Exception as e:
            self.fail("Failed to get current state: {0}".format(e.message))
        
        # We want the SslInitiationPolicy on the forum
        if self.state == 'present':
                        
            if have_state is not None:
                # It exists so we'll check it matches what we want
                
                if have_state == want_state:
                    # It exists and matches our desired state
                    
                    self.log(have_state.to_dict(), True)
                    changed = False
                    results = have_state.to_dict()
                else:
                    # It exists but requires an update to match our desired state
                    
                    # If the want state is None i.e we never specified it we'll treat it as if we do not care about its value.
                    # If the want state is not None i.e we did specify it we'll record it as delta that needs to be updated. 
                    found_deltas = dict()
                    
                    # get the props on this SslInitiationPolicy
                    for prop in have_state.swagger_types.keys():

                        
                        have_value = getattr(have_state, prop)
                        want_value = getattr(want_state, prop)

                        if want_value is not None:
                            # want state is Not None so if it doesnt match have we'll need add it to our deltas
                            if  have_value != want_value:
                                # have value doesnt match want value
                                delta = dict(acutal=have_value, want_value=want_value)
                                found_deltas.update(prop=delta)

                    if len(found_deltas) > 0:
                        # We have changes we care about.    
                        changed = True
                        results = want_state.to_dict()
                    else:
                        # We do not have any changes we care about.
                        changed = False
                        results = have_state.to_dict()
            else:
                # It doesnt exist so we'll create it
                
                changed = True
                results = want_state.to_dict()    
        
        # We do not want the SslInitiationPolicy on the forum    
        elif self.state == 'absent':
            
            if have_state is not None:
                # It exists so we'll remove it
                
                changed = True
            else:
                # It doesnt exist so we do not need to do anything
                
                changed = False
     
        else:
            self.fail("unsupported state: {0}".format(self.state))    
            
            
        
        self.results['changed'] = changed
        self.results['state'] = results

        # We've figured out if we need to do a change. If we aren't in check mode we now make it
        if not self.check_mode:
            # We arent in check mode so we'll make changes here if we need to
            
            if self.state == 'present' and changed:
                # Create/Update the SslInitiationPolicy
                try:
                    updated_state = api.set(self.name, want_state)
                    self.results['state'] = updated_state.to_dict()
                    
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
                        
            elif self.state == 'absent' and changed:
                # delete the SslInitiationPolicy
                try:
                    updated_state = api.delete(self.name)
                    self.results['state']['status'] = 'deleted'
                
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
            
                          
        return self.results


def main():
    FSentrySslInitiationPolicy()

if __name__ == '__main__':
    main()
