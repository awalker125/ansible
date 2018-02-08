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
module: fsentry_task_list
version_added: "2.4"
short_description: Manage forum sentry TaskList(s).
description:
    - Create, update or delete a TaskList.
    - Import/export a TaskList.
options:
    description:
        description:
            - Description to be added to the TaskList on the forum.
    enabled:
        description:
            - Should the TaskList be enabled on the forum?
        default: yes
        type: bool
extends_documentation_fragment:
    - fsentry_base
    - fsentry_fsg

author:
    - "Andrew Walker (@awalker125)"
    - "Andrew Partis (@partis)"
    - "Carl Stuart (@automation1002)"
'''

EXAMPLES = '''
#import

fsentry_task_list:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: fsg
  fsg_password: "********"
  src: "/tmp/hello_world.fsg"
  force: 'true'
  
#export

fsentry_task_list:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: fsg
  fsg_password: "********"
  dest: "/tmp/"
  force: 'true'

#create

fsentry_task_list:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: present
  description: "hello_world world"
  enabled: true

#remove

fsentry_task_list:
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
  description: current state of the TaskList.
  returned: on success
  type: complex
  contains:
      status:
          description: the status of the operation
          returned: when state is fsg or absent
          type: str
          sample:
              - deployed
              - exported
              - deleted
      enabled:
            description: the enabled state of the TaskList on the forum.
            returned: when state is present
            type: bool
            sample:
                - true
                - false
      description:
            description: the description of the TaskList on the forum.
            returned: when state is present
            type: str
            sample: "My Task List"
      name:
            description: the name of the TaskList on the forum.
            returned: when state present
            type: str
            sample: "my_task_list"
'''  # NOQA

from ansible.module_utils.network.fsentry.common import FSentryModuleBase

try:
    from forumsentry_api.models.task_list import TaskList
except ImportError:
    # This is handled in azure_rm_common
    pass

class FSentryTaskList(FSentryModuleBase):


    def __init__(self):

        # Additional args for this module
        self.module_arg_spec = dict(
            description=dict(type='str'),
            enabled=dict(type='bool', default=True),
            )

        self.module_required_if = [
            [ 'state' , 'present' , [ 'name' ] ],
            [ 'state' , 'absent' , [ 'name' ] ]
        ]


        self.results = dict(
            changed=False,
            state=dict()
        )

        # additional props for this module
        # These will have there values set as part of super().__init__
        self.description = None
        self.enabled = None



        super(FSentryTaskList, self).__init__(self.module_arg_spec,
                                            supports_check_mode=True,
                                            required_if=self.module_required_if,
                                            add_file_common_args=False
                                            )



    def exec_module(self, **kwargs):


        want_state = None
        have_state = None
        updated_state = None
   
        api = self.task_lists_api
        results = dict()
        changed = False

        
        
        # Get the current state
        try:
            have_state = api.get(self.name)
        except Exception as e:
            self.fail("Failed to get current state: {0}".format(e.message))
        
        # We want the TaskList on the forum
        if self.state == 'present':
            
                    
            try:
    
                want_state = TaskList(name=self.name, description=self.description, enabled=self.enabled) 
    
            except Exception as e:
                self.fail("Failed to create model for want state: {0}".format(e.message))                                 
                                                        
                 
                        
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
                    
                    # get the props on this TaskList
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
        
        # We do not want the TaskList on the forum    
        elif self.state == 'absent':
            
            if have_state is not None:
                # It exists so we'll remove it
                
                changed = True
            else:
                # It doesnt exist so we do not need to do anything
                
                changed = False
       
        


      
        # We want to do an import or export
        elif self.state == 'fsg':
            
            if self.src:
                # src arg provided we want to deploy to forum. (Note: we are relying on the module validation rules to ensure either src or dest is set with state=fsg)
                # 
                # 1. Check the src file is a file
                # 2. Check the src file is readable
                # 3. If have_state is not None the TaskList exists on the forum so:
                #    i. if force then upload
                #    ii. if not force then assume no changes are required
                #     
                
                # this will fail if its not a file and readable
                self.src_is_valid()
                # we want to import to the device
                if have_state is not None:
                    # the TaskList already exists. We will only import if force = true
                    if self.force:
                        changed = True
                    else:
                        self.module.warn("{0} exists. Use force to overwrite".format(self.name))
                        changed = False
                else:
                    # the TaskList doesnt exist so we should run the import. There is no way to validate that the import contains the TaskList we are interested in unfortunately
                    changed = True    
            else:
                # dest arg provided we want to export from the forum. (Note: we are relying on the module validation rules to ensure either src or dest is set with state=fsg)
                #
                # 1. If has_state is None then fail as nothing to export
                # 2. Check to see dest is a directory. If it is then make it a file called \"{0}/{1}.fsg\".format(self.dest,self.name)
                # 3. Check the directory we want to put the file in exists. If not try to create it. Fail if we cant
                # 4. See if the file exist already. If it does:
                #    ii. if force then download
                #    iii. if not force then assume no changes are required
                # 4. If the file doesnt exist changed = true

                
                if have_state is None:
                    self.fail("cannot export none existent TaskList {0}".format(self.name))
                
                # make sure our dest is a file not a directory.
                self.dest_as_file()
                
                # We already have a file here
                if os.path.isfile(self.dest):
                    if self.force:
                        changed = True
                    else:
                        changed = False
                        self.module.warn("{0} exists. Use force to overwrite".format(self.dest))
                else:
                    # We dont have the existing file
                    changed = True

     
        else:
            self.fail("unsupported state: {0}".format(self.state))    
            
            
        
        self.results['changed'] = changed
        self.results['state'] = results

        # We've figured out if we need to do a change. If we aren't in check mode we now make it
        if not self.check_mode:
            # We arent in check mode so we'll make changes here if we need to
            
            if self.state == 'present' and changed:
                # Create/Update the TaskList
                try:
                    updated_state = api.set(self.name, want_state)
                    self.results['state'] = updated_state.to_dict()
                    
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
                        
            elif self.state == 'absent' and changed:
                # delete the TaskList
                try:
                    updated_state = api.delete(self.name)
                    self.results['state']['status'] = 'deleted'
                
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
            
            elif self.state == 'fsg' and changed:
                # deploy/export mode
                
                if self.src:
                    # deploy fsg
                    
                    try:
                        api.deploy(self.src, self.fsg_password)
                        self.results['state']['status'] = 'deployed'
                        
                    except Exception as e:
                        self.fail("Failed to deploy fsg {0}: {1} ".format(self.src, e.message))
                else:
                    # export mode
                    
                    fsg_tmp = None
                    try:
                        dest_dir = os.path.dirname(self.dest)
                        
                        # check/create dest dir
                        if not os.path.isdir(dest_dir):
                            os.makedirs(dest_dir)
                        
                        # get a temp file name to download to
                        fsg_tmp = tempfile.mktemp(dir=dest_dir)
                        
                        # download to a temp file
                        api.export(self.name, fsg_tmp, self.fsg_password, self.agent)
                        
                        # move the temp file to the dest
                        self.module.atomic_move(fsg_tmp, self.dest)
                        
                    except (OSError, IOError) as e:
                        self.fail('The destination directory ({0}) is not writable by the current user. Error was: {1}'.format(os.path.dirname(self.dest), e.message))
                    except Exception as e:
                        self.fail("Failed to export TaskList: {0}".format(e.message))
                    finally:
                        # cleanup any temp files
                        if fsg_tmp is not None:
                            if os.path.isfile(fsg_tmp):
                                try:
                                    os.remove(fsg_tmp)
                                except Exception as e:
                                    # We couldnt cleanup for some reason but we will not fail
                                    pass
                        

                    self.results['state']['status'] = 'exported'
                          
        return self.results


def main():
    FSentryTaskList()

if __name__ == '__main__':
    main()
