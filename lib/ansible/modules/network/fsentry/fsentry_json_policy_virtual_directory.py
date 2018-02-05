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
module: fsentry_json_policy_virtual_directory
version_added: "2.4"
short_description: Manage forum sentry JsonPolicy virtual directory(s).
description:
    - Create, update or delete a JsonPolicy virtual directory(s)
options:
    description:
        description:
            - Description to be added to the JsonPolicy virtual directory object on the forum.
    parent:
        description:
            - The parent JsonPolicy on the forum. This must already exist.
        required: True
    remote_path:
        description:
            - The remote path to use   
    listener_policy:
        description:
            - The listener policy to use
    virtual_path:
        description:
            - The virtual path to use
    remote_policy:
        description:
            - The remote policy to use
            - required if I(use_remote_policy=true)
    request_process_type:
        description:
            - the type of request processing to use
        choices:
          - "TASK_LIST"
          - "TASK_LIST_GROUP"
    response_process_type:
        description:
            - the type of response processing to use 
        choices:
          - "TASK_LIST"
          - "TASK_LIST_GROUP"            
    request_process:
        description:
            - the task list or task list group to use for request processing        
    response_process:
        description:
            - the task list or task list group to use for response processing     
    error_template:
        description:
            - the error template to use            
    use_remote_policy:
        description:
            - use a remote policy
        type: bool     
    request_filter_policy:
        description:
            - the request filter policy to use
    enabled:
        description:
            - Should the virtual directory be enabled on the forum?
        type: bool
        default: yes                       
    virtual_host:
        description:
            - the virtual host to use
    acl_policy:
        description:
            - the acl policy to use
            
                                       
extends_documentation_fragment:
    - fsentry_base
    - fsentry_nofsg

author:
    - "Andrew Walker (@awalker125)"
    - "Andrew Partis (@partis)"
    - "Carl Stuart (@automation1002)"

notes:
    - The model for the JsonPolicies api on forum is called JsonPolicies not JsonPolicy
'''

EXAMPLES = '''
#create

fsentry_json_policies_virtual_directory:
  parent: hello_world
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: present
  description: "hello_world world"
  listener_policy: hello
  virtual_path: "/login"

  

#remove

fsentry_json_policies_virtual_directory:

  parent: hello_world
  name: "New Virtual Directory"
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
  description: current state of the JsonPolicies object.
  returned: on success
  type: complex
  contains:
      status:
          description: the status of the operation
          returned: when state is absent
          type: str
          sample:
              - deleted
      name:
          description: ""
          returned: when state present
          type: str
      remote_path:
          description: ""
          returned: when state is present
          type: str
      listener_policy:
          description: ""
          returned: when state is present
          type: str
      virtual_path:
          description: ""
          returned: when state is present
          type: bool
      remote_policy:
          description: ""
          returned: when state is present
          type: str
      description:
          description: ""
          returned: when state is present
          type: str
      request_process_type:
          description: ""
          returned: when state is present
          type: str
          samples:
            - "TASK_LIST"
            - "TASK_LIST_GROUP"
      response_process_type:
          description: ""
          returned: when state is present
          type: str
          samples:
            - "TASK_LIST"
            - "TASK_LIST_GROUP"
      error_template:
          description: ""
          returned: when state is present
          type: str
      request_process:
          description: ""
          returned: when state is present
          type: str
      response_process:
          description: ""
          returned: when state is present
          type: str
      request_filter_policy:
          description: ""
          returned: when state is present
          type: str
      virtual_host:
          description: ""
          returned: when state is present
          type: str   
      acl_policy:
          description: ""
          returned: when state is present
          type: str
      enabled:
          description: ""
          returned: when state is present
          type: bool
      use_remote_policy:
          description: ""
          returned: when state is present
          type: bool           
'''  # NOQA

from ansible.module_utils.network.fsentry.common import FSentryModuleBase

try:
    #from forumsentry_api.models.json_policies import JsonPolicies
    from forumsentry_api.models.virtual_directory import VirtualDirectory
except ImportError:
    # This is handled in azure_rm_common
    pass

class FSentryJsonPolicyVirtualDirectory(FSentryModuleBase):


    def __init__(self):

        # Additional args for this module
        self.module_arg_spec = dict(
            parent=dict(type='str',required=True),
            acl_policy=dict(type='str'),
            remote_path=dict(type='str'),
            virtual_host=dict(type='str'),
            enabled=dict(type='bool', default=True),
            description=dict(type='str'),
            request_process_type=dict(type='str', choices=['TASK_LIST', 'TASK_LIST_GROUP']),
            response_process_type=dict(type='str', choices=['TASK_LIST', 'TASK_LIST_GROUP']),
            listener_policy=dict(type='str'),
            request_process=dict(type='str'),
            response_process=dict(type='str'),
            request_filter_policy=dict(type='str'),
            remote_policy=dict(type='str'),
            use_remote_policy=dict(type='bool'),
            error_template=dict(type='str'),
            virtual_path=dict(type='str'),
#             state=dict(
#                 type='str',
#                 default='present',
#                 choices=['present', 'absent']
#                 )                     
            )


        self.module_required_if = [
            [ 'state' , 'present' , [ 'name' , 'parent' ] ],
            [ 'state' , 'absent' , [ 'name', 'parent' ] ],
            [ 'use_remote_policy' , 'true' , [ 'remote_policy' ] ],
        ]


        self.results = dict(
            changed=False,
            state=dict()
        )

        # additional props for this module
        # These will have there values set as part of super().__init__
        self.parent = None
        self.acl_policy = None
        self.remote_path = None
        self.virtual_host = None
        self.enabled = None
        self.description = None        
        self.request_process_type = None
        self.response_process_type = None
        self.listener_policy = None
        self.request_process = None
        self.response_process = None
        self.request_filter_policy = None
        self.remote_policy = None        
        self.use_remote_policy = None          
        self.error_template = None
        self.virtual_path = None       
        
        
                        
        super(FSentryJsonPolicyVirtualDirectory, self).__init__(self.module_arg_spec,
                                            supports_check_mode=True,
                                            required_if=self.module_required_if,
                                            add_file_common_args=False,
                                            fsg=False
                                            )



    def exec_module(self, **kwargs):

        want_state = VirtualDirectory(  name=self.name,
                                        acl_policy=self.acl_policy,
                                        remote_path=self.remote_path,
                                        virtual_host=self.virtual_host,
                                        enabled=self.enabled,
                                        description=self.description,
                                        request_process_type=self.request_process_type,
                                        response_process_type=self.response_process_type,
                                        listener_policy=self.listener_policy,
                                        request_process=self.request_process,
                                        response_process=self.response_process,
                                        request_filter_policy=self.request_filter_policy,
                                        remote_policy=self.remote_policy,
                                        use_remote_policy=self.use_remote_policy,
                                        error_template=self.error_template,
                                        virtual_path=self.virtual_path,                                                                                                                             
                                        )
                                        
                                        
                                        
        have_state = None
        updated_state = None
   
        api = self.json_policies_api
        results = dict()
        changed = False

        
        
        # Get the current state
        try:
            have_state = api.get_virtual_directory(self.parent,self.name)
        except Exception as e:
            self.fail("Failed to get current state: {0}".format(e.message))
        
        # We want the JsonPolicies on the forum
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
                    
                    # get the props on this JsonPolicies
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
        
        # We do not want the JsonPolicies on the forum    
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
                # Create/Update the JsonPolicies
                try:
                    updated_state = api.set_virtual_directory(self.parent,self.name, want_state)
                    self.results['state'] = updated_state.to_dict()
                    
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
                        
            elif self.state == 'absent' and changed:
                # delete the JsonPolicies
                try:
                    updated_state = api.delete_virtual_directory(self.parent, self.name)
                    self.results['state']['status'] = 'deleted'
                
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
                          
        
        return self.results


def main():
    FSentryJsonPolicyVirtualDirectory()

if __name__ == '__main__':
    main()
