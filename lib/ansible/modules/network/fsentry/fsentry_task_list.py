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
module: fsentry_have_state
version_added: "2.4"
short_description: Manage forum sentry task lists.
description:
    - Create, update or delete a task list.
options:
    resource_group:
        description:
            - Name of resource group.
        required: true
    name:
        description:
            - Name of the subnet.
        required: true
    address_prefix_cidr:
        description:
            - CIDR defining the IPv4 address space of the subnet. Must be valid within the context of the
              virtual network.
        required: true
        aliases:
            - address_prefix
    security_group_name:
        description:
            - Name of an existing security group with which to associate the subnet.
        required: false
        default: null
        aliases:
            - security_group
    state:
        description:
            - Assert the state of the subnet. Use 'present' to create or update a subnet and
              'absent' to delete a subnet.
        required: false
        default: present
        choices:
            - absent
            - present
    virtual_network_name:
        description:
            - Name of an existing virtual network with which the subnet is or will be associated.
        required: true
        aliases:
            - virtual_network

extends_documentation_fragment:
    - azure

author:
    - "Chris Houseknecht (@chouseknecht)"
    - "Matt Davis (@nitzmahone)"

'''

EXAMPLES = '''
    - name: Create a subnet
      azure_rm_subnet:
        name: foobar
        virtual_network_name: My_Virtual_Network
        resource_group: Testing
        address_prefix_cidr: "10.1.0.0/24"

    - name: Delete a subnet
      azure_rm_subnet:
        name: foobar
        virtual_network_name: My_Virtual_Network
        resource_group: Testing
        state: absent
'''

RETURN = '''
state:
    description: Current state of the subnet.
    returned: success
    type: complex
    contains:
        address_prefix:
          description: IP address CIDR.
          type: str
          example: "10.1.0.0/16"
        id:
          description: Subnet resource path.
          type: str
          example: "/subscriptions/XXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX/resourceGroups/Testing/providers/Microsoft.Network/virtualNetworks/My_Virtual_Network/subnets/foobar"
        name:
          description: Subnet name.
          type: str
          example: "foobar"
        network_security_group:
          type: complex
          contains:
            id:
              description: Security group resource identifier.
              type: str
              example: "/subscriptions/XXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX/resourceGroups/Testing/providers/Microsoft.Network/networkSecurityGroups/secgroupfoo"
            name:
              description: Name of the security group.
              type: str
              example: "secgroupfoo"
        provisioning_state:
          description: Success or failure of the provisioning event.
          type: str
          example: "Succeeded"
'''  # NOQA

from ansible.module_utils.network.fsentry.common import FSentryModuleBase

try:
    from forumsentry_api.models.task_list import TaskList
except ImportError:
    # This is handled in azure_rm_common
    pass

class FSentryTaskList(FSentryModuleBase):


    def __init__(self):

        #Additional args for this module
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

        want_state = TaskList(name=self.name, description=self.description, enabled=self.enabled) 
        have_state = None
        updated_state = None
   
        api = self.task_lists_api
        results = dict()
        changed = False
        #used by export 
        #fsg_tmp = None
        
        
        
        # Get the current state
        try:
            have_state = api.get(self.name)
        except Exception as e:
            self.fail("Failed to get current state: {0}".format(e.message))
        
        # We want the TaskList on the forum
        if self.state == 'present':
            self.log("state = present", False)
                
            if have_state is not None:
                self.log("It exists so we'll check it matches what we want", False)
                    # It exists so we'll check it matches what we want
                if have_state == want_state:
                    # It exists and matches our desired state
                    self.log("It exists and matches our desired state", False)
                    self.log(have_state.to_dict(),True)
                    changed = False
                    results = have_state.to_dict()
                else:
                    self.log("It exists but might requires an update to match our desired state", False)
                    # It exists but requires an update to match our desired state
                    
                    # If the want state is None i.e we never specified it we'll treat it as if we do not care about its value.
                    # If the want state is not Not i.e we did specify it we'll record it as delta that needs to be updated. 
                    
                    found_deltas = dict()
                    
                    # get the props on this object
                    for prop in have_state.swagger_types.keys():

                        
                        have_value = getattr(have_state, prop)
                        want_value = getattr(want_state, prop)

                        if want_value is not None:
                            # want state is Not None so if it doesnt match have we'll need add it too our deltas
                            if  have_value != want_value:
                                self.log("have_value {1} {0}".format(have_value, prop))
                                self.log("want_value {1} {0}".format(want_value, prop))
                                delta = dict(acutal=have_value, want_value=want_value)
                                found_deltas.update(prop=delta)
                            else:
                                self.log("prop {0} matches".format(prop))
                        else:
                            # want state is None so we do not care what its value is    
                            self.log("have_value {1} {0}".format(have_value, prop))
                            self.log("want_value {0} is None".format(prop))

                    if len(found_deltas) > 0:    
                        changed = True
                        results = want_state.to_dict()
                    else:
                        changed = False
                        results = have_state.to_dict()
            else:
                self.log("It doesnt exist so we'll create it", False)
                # It doesnt exist so we'll create it
                changed = True
                # Set the results to the want state. We'll update this if check mode is false
                results = want_state.to_dict()    
        
        # We do not want the TaskList on the forum    
        elif self.state == 'absent':
            self.log("state = absent", False)
            if have_state is not None:
                self.log("It exists so we'll remove it", False)
                # It exists so we'll remove it
                changed = True
            else:
                self.log("It doesnt exist so we do not need to do anything", False)
                # It doesnt exist so we do not need to do anything
                changed = False
        #We want to export the config from the device
        

        #src arg provided we want to deploy to forum
        # 
        #1. Check the src file is a file
        #2. Check the src file is readable
        #3. If have_state is not None the object exists on the forum so:
        #    i. if force then upload
        #    ii. if force then assume no changes are required
        #         
        #dest arg provided we want to export from the forum
        #
        #1. If has_state is None then fail as nothing to export
        #2. Check to see dest is a directory. If it is then make it a file called \"{0}/{1}.fsg\".format(self.dest,self.name)
        #3. Check the directory we want to put the file in exists. If not try to create it. Fail if we cant
        #4. download the fsg to a temp file and generate an sha1 hash of it

        #4. See if the file exist already. If it does:
        #    ii. check the sha1 hash of the existing file. If it matched then changed is false and remove temp file
        #    iii. if the sha1 hash doesnt match and force is false then fail warning of the mismatch.
        #    iiii. if the sha1 hash doesnt match and force is true then backup the existing fsg and copy the temp one over the top.
        #4. If the file doesnt exist changed = true

        #6. If the directory does exist then copy our temp file into

        
                
        elif self.state == 'fsg':
            self.log("state = fsg", False)
            
            if self.src:
                #this will fail if its not a file and readable
                self.src_is_valid()
                #we want to import to the device
                if have_state is not None:
                    #the object already exists. We will only import if force = true
                    if self.force:
                        changed = True
                    else:
                        self.module.warn("{0} exists. Use force to overwrite".format(self.name))
                        changed = False
                else:
                    #the object doesnt exist so we should run the import. There is no way to validate that the import contains the object we are interested in unfortunately
                    changed = True    
            else:
                #make sure our dest is a file not a directory
                self.dest_as_file()
                #we want to export from the device
                if have_state is not None:
                                      
                    #We already have a file here
                    if os.path.isfile(self.dest):
                        if self.force:
                            changed = True
                        else:
                            changed = False
                            self.module.warn("{0} exists. Use force to overwrite".format(self.dest))
                    else:
                        #We dont have the existing file
                        changed = True
                else:
                    self.fail("cannot export none existent object {0}".format(self.name))
     
        else:
            self.fail("unsupported state: {0}".format(self.state))    
            
            
        
        self.results['changed'] = changed
        self.results['state'] = results

        # We've figured out if we need to do a change. If we aren't in check mode we now make it
        if not self.check_mode:
            self.log("check_mode == false")
            if self.state == 'present' and changed:
                self.log(want_state.to_dict(), pretty_print=True)

                try:
                    updated_state = api.set(self.name, want_state)
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
                    
                self.log(updated_state.to_dict(), pretty_print=True)
                
                self.results['state'] = updated_state.to_dict()
            elif self.state == 'absent' and changed:
                # delete if we need to
                try:
                    updated_state = api.delete(self.name)
                    self.results['state']['status'] = 'deleted'
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
            elif self.state == 'fsg' and changed:
                if self.src:
                    try:
                        api.deploy(self.src, self.fsg_password)
                        self.results['state']['status'] = 'deployed'
                    except Exception as e:
                        self.fail("Failed to deploy fsg {0}: {1} ".format(self.src, e.message))
                else:
                    
                    fsg_tmp = None
                    try:
                        dest_dir = os.path.dirname(self.dest)
                        if not os.path.isdir(dest_dir):
                            os.makedirs(dest_dir)
                        
                        fsg_tmp = tempfile.mktemp(dir=dest_dir)
                        self.log("fsg_tmp {0}".format(fsg_tmp))
                        
                        exported = api.export(self.name, fsg_tmp, self.fsg_password, self.agent)
                        
                        self.log("exported {0}".format(str(exported)))
                        
                        self.module.atomic_move(fsg_tmp,self.dest)
                        
                    except (OSError, IOError) as e:
                        self.fail('The destination directory ({0}) is not writable by the current user. Error was: {1}'.format(os.path.dirname(self.dest), e.message))
                    except Exception as e:
                        self.fail("Failed to export object: {0}".format(e.message))
                    finally:
                        #cleanup any temp files
                        if fsg_tmp is not None:
                            if os.path.isfile(fsg_tmp):
                                try:
                                    os.remove(fsg_tmp)
                                except Exception as e:
                                    #We couldnt cleanup for some reason but we will not fail
                                    pass
                        

                    self.results['state']['status'] = 'exported'
                    

                          
        return self.results


def main():
    FSentryTaskList()

if __name__ == '__main__':
    main()
