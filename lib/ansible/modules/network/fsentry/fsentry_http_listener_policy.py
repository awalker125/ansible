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
module: fsentry_http_listener_policy
version_added: "2.4"
short_description: Manage forum sentry HttpListenerPolicy(s).
description:
    - Create, update or delete a HttpListenerPolicy.
    - Import/export a HttpListenerPolicy.
options:
    description:
        description:
            - Description to be added to the HttpListenerPolicy on the forum.
    use_cookie_authentication:
        description:
            - Enable cookie authentication
        type: bool
    use_digest_authentication:
        description:
            - Enable digest authentication
        type: bool
    use_basic_authentication:
        description:
            - Enable basic authentication
        type: bool
    use_form_post_authentication:
        description:
            - Enable form post authentication
        type: bool
    enabled:
        description:
            - Should the HttpListenerPolicy be enabled on the forum?
        type: bool
        default: yes        
    listener_ssl_enabled:
        description:
            - Enable ssl
        type: bool
    require_password_authentication:
        description:
            - Require password authentication
        type: bool      
    use_kerberos_authentication:
        description:
            - Enable kerberos authentication
        type: bool 
    use_chunking:
        description:
            - Enable http chunking
        type: bool         
    use_device_ip:
        description:
            - Use the device ip
        type: bool             
    acl_policy:
        description:
            - the acl policy to use
    ip_acl_policy:
        description:
            - the ip acl policy to use
        default: Unrestricted
    password_parameter:
        description:
            - the password pararmeter to use         
    listener_ssl_policy:
        description:
            - the listener ssl policy to use        
    username_parameter:
        description:
            - the username parameter to use         
    interface:
        description:
            - the interface to use
        choice:
            - LAN
            - WAN
        default: WAN   
    error_template:
        description:
            - the error template to use
        default: "Default Template"    
    listener_host:
        description:
            - the listener host to use             
    read_timeout_millis:
        description:
            - the network read timeout to set on the listener
        type: int                
    password_authentication_realm:
        description:
            - the realm to use with password authentication
    port:
        description:
            - the port for the listener
        type: int                          
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

fsentry_http_listener_policy:
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

fsentry_http_listener_policy:
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

fsentry_http_listener_policy:
  name: hello_world
  fsentry_protocol: http
  fsentry_host: forumsentry-dev
  fsentry_port: '8081'
  fsentry_username: admin
  fsentry_password: "********"
  fsentry_verify_ssl: false
  state: present
  description: "hello_world world"
  port: 8088
  

#remove

fsentry_http_listener_policy:
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
  description: current state of the HttpListenerPolicy.
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
      name:
          description: ""
          returned: when state present
          type: str
      description:
          description: ""      
          returned: when state is present
          type: str
      use_chunking:
          description: ""
          returned: when state is present
          type: str
      use_basic_authentication:
          description: ""
          returned: when state is present
          type: str
      username_parameter:
          description: ""
          returned: when state is present
          type: str
      use_device_ip:
          description: ""
          returned: when state is present
          type: str
      password_parameter:
          description: ""
          returned: when state is present
          type: str
      listener_host:
          description: ""
          returned: when state is present
          type: str
      port:
          description: ""
          returned: when state is present
          type: int
      use_digest_authentication:
          description: ""
          returned: when state is present
          type: bool
      use_cookie_authentication:
          description: ""
          returned: when state is present
          type: bool
      read_timeout_millis:
          description: ""
          returned: when state is present
          type: int
      password_authentication_realm:
          description: ""
          returned: when state is present
          type: str
      use_kerberos_authentication:
          description: ""
          returned: when state is present
          type: bool
      listener_ssl_enabled:
          description: ""
          returned: when state is present
          type: bool
      require_password_authentication:
          description: ""
          returned: when state is present
          type: bool
      interface:
          description: ""
          returned: when state is present
          type: str
          samples:
              - WAN
              - LAN
      listener_ssl_policy:
          description: ""
          returned: when state is present
          type: str
      error_template:
          description: ""
          returned: when state is present
          type: str
          samples:
              -  "Default Template"
      use_kerberos_authentication:
          description: ""
          returned: when state is present
          type: bool
      acl_policy:
          description: ""
          returned: when state is present
          type: str
      enabled:
          description: ""
          returned: when state is present
          type: bool
      ip_acl_policy:
          description: ""
          returned: when state is present
          type: str
          samples:
              - "Unrestricted"
      use_form_post_authentication:
          description: ""
          returned: when state is present
          type: bool            
'''  # NOQA

from ansible.module_utils.network.fsentry.common import FSentryModuleBase

try:
    from forumsentry_api.models.http_listener_policy import HttpListenerPolicy
except ImportError:
    # This is handled in azure_rm_common
    pass

class FSentryHttpListenerPolicy(FSentryModuleBase):


    def __init__(self):

        # Additional args for this module
        self.module_arg_spec = dict(
            description=dict(type='str'),
            use_cookie_authentication=dict(type='bool'),
            use_digest_authentication=dict(type='bool'),
            use_basic_authentication=dict(type='bool'),
            use_form_post_authentication=dict(type='bool'),
            enabled=dict(type='bool', default=True),
            listener_ssl_enabled=dict(type='bool'),
            require_password_authentication=dict(type='bool'),
            use_kerberos_authentication=dict(type='bool'),
            use_chunking=dict(type='bool'),
            acl_policy=dict(type='str'),
            ip_acl_policy=dict(type='str',
                               default="Unrestricted"),
            password_parameter=dict(type='str', no_log=True),
            use_device_ip=dict(type='bool'),
            listener_ssl_policy=dict(type='str'),
            username_parameter=dict(type='str'),
            interface=dict(type='str',
                           default='WAN',
                           choices=['WAN', 'LAN']),
            error_template=dict(type='str',
                                default="Default Template"),
            listener_host=dict(type='str'),
            read_timeout_millis=dict(type='int'),
            password_authentication_realm=dict(type='str', no_log=True),
            port=dict(type='int')
            )


        self.module_required_if = [
            [ 'state' , 'present' , [ 'name' ] ],
            [ 'state' , 'absent' , [ 'name' ] ],
            [ 'listener_ssl_enabled' , 'true' , [ 'listener_ssl_policy' ] ],
            [ 'use_device_ip' , 'false' , [ 'interface' ] ],
        ]


        self.results = dict(
            changed=False,
            state=dict()
        )

        # additional props for this module
        # These will have there values set as part of super().__init__
        self.description = None
        self.use_cookie_authentication = None
        self.use_basic_authentication = None
        self.acl_policy = None
        self.ip_acl_policy = None        
        self.read_timeout_millis = None
        self.password_parameter = None
        self.use_digest_authentication = None
        self.use_chunking = None
        self.port = None
        self.use_device_ip = None
        self.use_form_post_authentication = None
        self.listener_ssl_policy = None
        self.username_parameter = None
        self.enabled = None
        self.interface = None      
        self.error_template = None
        self.listener_host = None
        self.listener_ssl_enabled = None
        self.password_authentication_realm = None
        self.require_password_authentication = None       
        self.use_kerberos_authentication = None          
                
        super(FSentryHttpListenerPolicy, self).__init__(self.module_arg_spec,
                                            supports_check_mode=True,
                                            required_if=self.module_required_if,
                                            add_file_common_args=False
                                            )



    def exec_module(self, **kwargs):

        want_state = None   
        have_state = None
        updated_state = None
   
        api = self.http_listener_policy_api
        results = dict()
        changed = False

        
        
        # Get the current state
        try:
            have_state = api.get(self.name)
        except Exception as e:
            self.fail("Failed to get current state: {0}".format(e.message))
        
        # We want the HttpListenerPolicy on the forum
        if self.state == 'present':
                 
            try:
    
                want_state = HttpListenerPolicy(name=self.name,
                                            description=self.description,
                                            use_cookie_authentication=self.use_cookie_authentication,
                                            use_basic_authentication=self.use_basic_authentication,
                                            acl_policy=self.acl_policy,
                                            ip_acl_policy=self.ip_acl_policy,
                                            read_timeout_millis=self.read_timeout_millis,
                                            password_parameter=self.password_parameter,
                                            use_digest_authentication=self.use_digest_authentication,
                                            use_chunking=self.use_chunking,
                                            port=self.port,
                                            use_device_ip=self.use_device_ip,
                                            use_form_post_authentication=self.use_form_post_authentication,
                                            listener_ssl_policy=self.listener_ssl_enabled,
                                            username_parameter=self.username_parameter,
                                            enabled=self.enabled,
                                            interface=self.interface,
                                            error_template=self.error_template,
                                            listener_host=self.listener_host,
                                            listener_ssl_enabled=self.listener_ssl_enabled,
                                            password_authentication_realm=self.password_authentication_realm,
                                            require_password_authentication=self.require_password_authentication,
                                            use_kerberos_authentication=self.use_kerberos_authentication
                                            )
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
                    
                    # get the props on this HttpListenerPolicy
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
        
        # We do not want the HttpListenerPolicy on the forum    
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
                # 3. If have_state is not None the HttpListenerPolicy exists on the forum so:
                #    i. if force then upload
                #    ii. if not force then assume no changes are required
                #     
                
                # this will fail if its not a file and readable
                self.src_is_valid()
                # we want to import to the device
                if have_state is not None:
                    # the HttpListenerPolicy already exists. We will only import if force = true
                    if self.force:
                        changed = True
                    else:
                        self.module.warn("{0} exists. Use force to overwrite".format(self.name))
                        changed = False
                else:
                    # the HttpListenerPolicy doesnt exist so we should run the import. There is no way to validate that the import contains the HttpListenerPolicy we are interested in unfortunately
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
                    self.fail("cannot export none existent HttpListenerPolicy {0}".format(self.name))
                
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
                # Create/Update the HttpListenerPolicy
                try:
                    updated_state = api.set(self.name, want_state)
                    self.results['state'] = updated_state.to_dict()
                    
                except Exception as e:
                    self.fail("Failed to update state: {0} ".format(e.message))
                        
            elif self.state == 'absent' and changed:
                # delete the HttpListenerPolicy
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
                        self.fail("Failed to export HttpListenerPolicy: {0}".format(e.message))
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
    FSentryHttpListenerPolicy()

if __name__ == '__main__':
    main()
