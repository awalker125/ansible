#!/usr/bin/python
#
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import os
import logging

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.six.moves import configparser
import ansible.module_utils.six.moves.urllib.parse as urlparse


FSENTRY_SDK_MIN_RELEASE = '0.12.128'
REQUESTS_MIN_RECOMMENDED_RELEASE = '2.18.4'


FSENTRY_COMMON_ARGS = dict(
    fsentry_host=dict(
        type='str',
        required=True,
        fallback=(env_fallback, ['FSENTRY_HOST'])
    ),
    fsentry_username=dict(
        type='str',
        aliases=['user'],
        required=True,
        fallback=(env_fallback, ['FSENTRY_USERNAME'])
    ),
    fsentry_password=dict(
        type='str',
        aliases=['pass', 'pwd'],
        required=True,
        no_log=True,
        fallback=(env_fallback, ['FSENTRY_PASSWORD'])
    ),
    fsentry_verify_ssl=dict(
        default='yes',
        type='bool',
        fallback=(env_fallback, ['FSENTRY_VERIFY_SSL'])
    ),
    fsentry_port=dict(
        type='int',
        default=443,
        fallback=(env_fallback, ['FSENTRY_PORT'])
    ),
    fsentry_context=dict(
        type='str',
        default='/restApi/v1.0',
        fallback=(env_fallback, ['FSENTRY_CONTEXT'])
    ),
    fsentry_protocol=dict(
        type='str',
        default='https',
        choices=['http', 'https'],
        fallback=(env_fallback, ['FSENTRY_PROTOCOL'])
    ),
    name=dict(
        type='str',
        required=True      
    ),
    state=dict(
        type='str',
        default='present',
        choices=['present', 'absent', 'fsg']
               
    ),
    fsg_password=dict(
        type='str',
        aliases=['fsg_pass'],
        no_log=True,
    ),
    force=dict(
        default='no',
        type='bool'
    ),
    src=dict(
        type='path'
    ),
    dest=dict(
        type='path'
    ),
    agent=dict(
        type='str'
    ),
    debug=dict(type='bool', default=False)
)

FSENTRY_COMMON_REQUIRED_IF = [
  [ "state", "present", [ "name" ] ],
  [ "state", "absent", [ "name" ] ],
  [ "state", "fsg", [ "name", "fsg_password" ] ]
]

FSENTRY_COMMON_REQUIRED_TOGETHER = []

FSENTRY_COMMON_MUTUALLY_EXCLUSIVE = [('src', 'dest')]

HAS_FSENTRY_SDK = True
HAS_REQUESTS = True

try:
    from forumsentry.task_lists_api import TaskListsApi
    from forumsentry.config import Config

    HAS_FSENTRY_SDK = True
except ImportError as e:

    HAS_FSENTRY_SDK = False

try:
    from requests import HTTPError
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class FSentryModuleBase(object):
    def __init__(self, derived_arg_spec, bypass_checks=False, no_log=False,
                 check_invalid_arguments=None, mutually_exclusive=None, required_together=None,
                 required_one_of=None, add_file_common_args=False, supports_check_mode=False,
                 required_if=None, skip_exec=False):

        merged_arg_spec = dict()
        merged_arg_spec.update(FSENTRY_COMMON_ARGS)


        if derived_arg_spec:
            merged_arg_spec.update(derived_arg_spec)

        merged_required_if = list(FSENTRY_COMMON_REQUIRED_IF)
        if required_if:
            merged_required_if += required_if
        
        merged_required_together = list(FSENTRY_COMMON_REQUIRED_TOGETHER)
        if required_together:
            merged_required_together += required_together
            
        merged_mutually_exclusive = list(FSENTRY_COMMON_MUTUALLY_EXCLUSIVE)
        if mutually_exclusive:
            merged_mutually_exclusive += mutually_exclusive  

        self.module = AnsibleModule(argument_spec=merged_arg_spec,
                                    bypass_checks=bypass_checks,
                                    no_log=no_log,
                                    check_invalid_arguments=check_invalid_arguments,
                                    mutually_exclusive=merged_mutually_exclusive,
                                    required_together=required_together,
                                    required_one_of=required_one_of,
                                    add_file_common_args=add_file_common_args,
                                    supports_check_mode=supports_check_mode,
                                    required_if=merged_required_if)
        

        

        if not HAS_FSENTRY_SDK:
            self.fail("Do you have forumsentry>={0} installed? Try `pip install forumsentry`".format(FSENTRY_SDK_MIN_RELEASE))

        if not HAS_REQUESTS:
            self.fail("Do you have requests>={0} installed? Try `pip install requests`".format(REQUESTS_MIN_RECOMMENDED_RELEASE))

        
        # common params
        self.state = None
        self.name = None
        self.force = None
        self.src = None
        self.dest = None
        self.agent = None
        
        # set our args as params
        for key in merged_arg_spec:
            setattr(self, key, self.module.params[key])
        
        self.check_mode = self.module.check_mode
        
        #init config used to connect to forum
        self._config = self._get_config(self.module.params)

        # apis
        self._task_lists_api = None
        
        # There does not seem to be a way to implement a nested required_if and required_one_of
        if self.state == "fsg":
            if self.src is None and self.dest is None:
                
                self.fail("one of src or dest is required with state fsg")

        if not skip_exec:
            res = self.exec_module(**self.module.params)
            self.module.exit_json(**res)


    def exec_module(self, **kwargs):
        self.fail("Error: {0} failed to implement exec_module method.".format(self.__class__.__name__))


    def fail(self, msg, **kwargs):
        '''
        Shortcut for calling module.fail()

        :param msg: Error message text.
        :param kwargs: Any key=value pairs
        :return: None
        '''
        self.module.fail_json(msg=msg, **kwargs)


    def src_is_valid(self):
        if not os.path.isfile(self.src):
            self.fail("The source path must be a file.")
        try:
            fp = open(self.src, 'r')
            fp.close()
        except IOError:
            self.fail("Failed to access {0}. Make sure the file exists and that you have "
                      "read access.".format(self.src))
        return True
    
    def dest_as_file(self):
        '''
        Converts dest to a file in case we get passed a directory
        '''
        #self.log("dest_as_file")
        
        if os.path.exists(self.dest):
            if os.path.isdir(self.dest):
                #self.log("{0} exists and is directory".format(self.dest))
                if not self.dest.endswith("/"):
                    self.dest = "{0}/{1}.fsg".format(self.dest, self.name)
                else:
                    self.dest = "{0}{1}.fsg".format(self.dest, self.name)
                #self.log("new dest {0}".format(self.dest))
        else:
            #self.log(type(os.path.basename(self.dest)))
            if not os.path.basename(self.dest):
                # os.path.basename returns "" if the path ends in /
                #self.log("{0} doesnt exists but looks like we want a directory".format(self.dest))
                self.dest = "{0}{1}.fsg".format(self.dest, self.name)
            else:
                # should we check for an append .fsg
                #self.log("{0} doesnt exists but looks like we have specified a file".format(self.dest))
                pass




    def _get_config(self, params):
        '''
        Helper to create a config object from module args
        '''
        _fsentry_protocol = params.get('fsentry_protocol')
        _fsentry_host = params.get('fsentry_host')
        _fsentry_port = params.get('fsentry_port')
        _fsentry_context = params.get('fsentry_context')
        _fsentry_username = params.get('fsentry_username')
        _fsentry_password = params.get('fsentry_password')
        _fsentry_verify_ssl = params.get('fsentry_verify_ssl')
        
        return Config(_fsentry_host, _fsentry_port, _fsentry_protocol, _fsentry_context, _fsentry_username, _fsentry_password, _fsentry_verify_ssl)
        
    @property
    def task_lists_api(self):
        '''
        Task list api property
        '''
        if not self._task_lists_api:
            self._task_lists_api = TaskListsApi(config=self._config)
        return self._task_lists_api


    def log(self, msg, pretty_print=False):
        # pass
        # Use only during module development
        l = logging.getLogger("ansible")
        if pretty_print:
            l.debug(json.dumps(msg, indent=4, sort_keys=True))
        else:
            l.debug(msg)

