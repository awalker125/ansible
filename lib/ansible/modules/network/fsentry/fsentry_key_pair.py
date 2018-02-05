#!/usr/bin/python
#
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import os
import tempfile

__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: fsentry_key_pair
version_added: "2.4"
short_description: Manage forum sentry KeyPair(s).
description:
    - Import or delete a KeyPair.
options:
    p12:
        description:
            - Description to be added to the KeyPair on the forum.
            - Required if I(state=present)
        type: path
    p12_password:
        description:
            - The password for the p12 file
            - Required if I(state=present)
        type: str
    private_key_password:
        description:
            - The password for the private key in the p12
            - Required if I(state=present)
        type: str    
    create_signer_group:
        description:
            - If a signer group should be created
        type: bool
        default: true
extends_documentation_fragment:
    - fsentry_base
    - fsentry_nofsg

notes:
    - forum does not support overwriting a key pair.
    - to update a key use I(state=absent) to delete the key and I(state=present) to reload.


author:
    - "Andrew Walker (@awalker125)"
    - "Andrew Partis (@partis)"
    - "Carl Stuart (@automation1002)"
'''

EXAMPLES = '''

#create

fsentry_key_pair:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: present
  p12: /path/to/your/keypair.p12
  p12_password: "********"
  private_key_password: "********"

#remove

fsentry_key_pair:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: absent
'''

RETURN = '''
state:
  description: current state of the KeyPair.
  returned: on success
  type: complex
  contains:
      status:
          description: the status of the operation
          returned: when I(state=present) or I(state=absent) and I(changed==true)
          type: str
          sample:
              - deployed
              - deleted
'''  # NOQA

from ansible.module_utils.network.fsentry.common import FSentryModuleBase


class FSentryKeyPair(FSentryModuleBase):


    def __init__(self):

        # Additional args for this module
        self.module_arg_spec = dict(
            p12=dict(type='path'),
            p12_password=dict(type='str', no_log=True),
            private_key_password=dict(type='str', no_log=True),
            create_signer_group=dict(type='bool',default=True)
            )

        self.module_required_if = [
            [ 'state' , 'present' , [ 'name','p12','p12_password','private_key_password' ] ],
            [ 'state' , 'absent' , [ 'name' ] ]
        ]


        self.results = dict(
            changed=False,
            state=dict()
        )

        # additional props for this module
        # These will have there values set as part of super().__init__
        self.p12 = None
        self.p12_password = None
        self.private_key_password = None
        self.create_signer_group = None


        super(FSentryKeyPair, self).__init__(self.module_arg_spec,
                                            supports_check_mode=True,
                                            required_if=self.module_required_if,
                                            add_file_common_args=False,
                                            fsg=False
                                            )



    def exec_module(self, **kwargs):

        have_state = None
   
        api = self.key_pairs_api
        results = dict()
        changed = False

        
        
        # Get the current state
        try:
            have_state = api.get(self.name)
        except Exception as e:
            self.fail("Failed to get current state: {0}".format(e.message))
        
        # We want the KeyPair on the forum
        if self.state == 'present':
            
            #This will fail if we cant find/read the p12 file
            self.p12_is_valid()
                        
            if have_state is not None:
                
                # the KeyPair already exists. 
                changed = False   
            else:
                # It doesnt exist so we'll create it
                changed = True
        
        # We do not want the KeyPair on the forum    
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
            #We arent in check mode so we'll make changes here if we need to
            
            if self.state == 'present' and changed:
                #Create/Update the KeyPair
                try:
                    api.pkcs12(self.name, self.p12, self.p12_password, self.private_key_password,create_signer_group=self.create_signer_group)
                    self.results['state']['status'] = 'deployed'
                    
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
                        
            elif self.state == 'absent' and changed:
                # delete the KeyPair
                try:
                    api.delete(self.name)
                    self.results['state']['status'] = 'deleted'
                
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
            
        return self.results

    def p12_is_valid(self):
        if not os.path.isfile(self.p12):
            self.fail("The p12 path must be a file.")
        try:
            fp = open(self.p12, 'r')
            fp.close()
        except IOError:
            self.fail("Failed to access {0}. Make sure the file exists and that you have "
                      "read access.".format(self.p12))
        return True

def main():
    FSentryKeyPair()

if __name__ == '__main__':
    main()
