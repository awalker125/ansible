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
notes:
  - Setting C(FSENTRY_DEBUG=true) will output low level calls to the forum for debugging purposes to stderr.
  - Requires the forumsentry Python package on the ansible host. Use C(pip install forumsentry).
requirements:
  - forumsentry >= 1.0.0
  - requests
  - jmespath
'''
