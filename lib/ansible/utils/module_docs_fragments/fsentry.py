# -*- coding: utf-8 -*-
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


class ModuleDocFragment(object):
    # Standard fsentry documentation fragment
    DOCUMENTATION = '''
options:
  fsentry_host:
    description:
      - The forum sentry host. You can omit this option if the environment
        variable C(FSENTRY_HOST) is set.
    required: true
  fsentry_username:
    description:
      - The username to connect to the REST API with. You can omit this option
        if the environment variable C(FSENTRY_USERNAME) is set.
    required: true  
  fsentry_password:
    description:
      - The password for the user account used to connect to the forumsentry REST API.
        You can omit this option if the environment variable C(FSENTRY_PASSWORD)
        is set.
    required: true
    aliases: ['pass', 'pwd']
  fsentry_verify_ssl:
    description:
      - If C(no), SSL certificates will not be validated. Use this only
        on personally controlled sites using self-signed certificates.
        You can omit this option if the environment variable
        C(FSENTRY_VERIFY_SSL) is set.
    default: yes
    type: bool
  fsentry_port:
    description:
      - The forum sentry rest api port. You can omit this option if the environment
        variable C(FSENTRY_PORT) is set.
    default: 443
  fsentry_context:
    description:
      - The context path of the rest api service on the forum sentry. You can omit this option if the environment
        variable C(FSENTRY_CONTEXT) is set.
    default: /restApi/v1.0
  fsentry_protocol:
    description:
      - The protocol to use to connect to forum sentry. You can omit this option if the environment
        variable C(FSENTRY_PROTOCOL) is set.
    default: https
    choices:
      - https
      - http
  name:
    description:
      - The name of the object on the forum sentry to manage.
    required: true
  state:
    description:
      - Assert the state of the forum sentry object.
      - If I(state=absent) the object will be deleted from forum if it exists.
      - If I(state=present) the object will be created/updated on the forum to match the module arguments. Optional arguments which are not provided will not be updated.
      - If I(state=fsg) import/export an fsg of the object. Use with either I(src) or I(dest)
    default: present
    choices:
      - present
      - absent
      - fsg
  fsg_password:
    description:
      - The password to decrypt/encrypt the fsg file with.
      - Required if I(state=fsg)
  force:
    description:
      - Used if I(state=fsg).
      - Force the import/export of the fsg regardless of if the object/fsg already exists.
    default: no
    type: bool
  src:
    description:
      - Used if I(state=fsg). 
      - Mutually exclusive with I(dest)
      - If set then the fsg will be imported to the forum.
      - Must be an fsg filepath.
      - If the object already exists on the forum with that name/type then import will be skipped unless I(force=true)
    type: path
  dest:
    description:
      - Used if I(state=fsg). 
      - Mutually exclusive with I(src)
      - If set then the object will be export to an fsg at the given path.
      - Can be either a filepath or a directory. 
      - If I(dest) is a directory then I(name).fsg will be used as the name of the export in that directory.
      - If the filepath already exists then this will not be overwritten unless I(force=true)
    type: path
  agent:
    description:
      - Used if I(state=fsg) and I(dest!=None)
      - The agent to use when exporting an object to an fsg. 
      - If unset then the default agent will be used.
      - Agent must exist on the forum.
      - This can be useful if you need to restrict what is exported e.g create a custom agent that disables data source param export.
    
notes:
  - Setting C(FSENTRY_DEBUG=true) will output low level calls to the forum for debugging purposes.
  - Requires the forumsentry Python package on the ansible host. This is as easy as C(pip install forumsentry).
requirements:
  - forumsentry >= 1.0.0
  - requests
'''
