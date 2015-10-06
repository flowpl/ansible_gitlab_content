#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: gitlab_user
short_description: create , update or delete a user account in Gitlab
options:
  username:
    description: The username to identify the account being altered
    required: yes
    default: none
    choices: []
  private_token:
    description: The private_token used for API authentication, it must belong to an admin user. Login to Gitlab and go to I(profile settings -> account) to find the private token.
    required: yes
    default: none
    choices: []
  api_url:
    description: the URL of the Gitlab API. e.g. U(http://gitlab.somedomain.com/api/v3)
    required: yes
    default: none
    choices: []
  name:
    description: the user's full name
    required: yes if the account does not exist yet
    default: none
    choices: []
  email:
    description: the user's email. This module only supports one email address per user. See the M(gitlab_email) module if you need more.
    required: yes if the account does not exist yet
    default: none
    choices: []
  password:
    description: the user's password. Be aware that if password is set, the module will always send an update request to Gitlab, regardless of whether something changed or not.
    required: yes if the account does not exist yet
    default: none
    choices: []
  skype:
    description: The user's skype
    required: no
    default: none
    choices: []
  linkedin:
    description: The user's linkedin profile
    required: no
    default: none
    choices: []
  twitter:
    description: The user's Twitter name
    required: no
    default: none
    choices: []
  website_url:
    description: The users website URL
    required: no
    default: none
    choices: []
  projects_limit:
    description: The users project limit. The default is none so the Gitlab default project_limit is used.
    required: no
    default: none
    choices: []
  bio:
    description: The users biographic text
    required: no
    default: none
    choices: []
  admin:
    description: whether the user is an admin user
    required: no
    default: no
    choices: [yes, no]
  can_create_group:
    description: whether the user can create groups. The default is none so the Gitlab default can_create_group is used.
    required: no
    default: none
    choices: [yes, no]
  state:
    description:
    required: no
    default: present
    choices: [present, absent]
  ssh_key_title:
    description: The title for the ssh key.
    required: yes if ssh_key is given
    default: none
    choices: []
  ssh_key:
    description: An SSH public key as a string. This module only supports one SSH key per user. See the M(gitlab_pubkey) module if you need more.
    required: no
    default: none
    choices: []
'''

EXAMPLES = '''
# create a new user, given that username is not yet used
- gitlab_user:
    username: test
    password: abc123yz
    name: some name
    email: someone@something.com
    api_url: https://gitlab-url-internal.somedomain.com/api/v3
    private_token: 7389rz478
    state: present


# change user test's email
- gitlab_user:
    username: test
    email: someone_else@something.com
    api_url: https://gitlab-url-internal.somedomain.com/api/v3
    private_token: 7389rz478
    state: present


# delete the user 'test'
- gitlab_user:
    username: test
    api_url: https://gitlab-url-internal.somedomain.com/api/v3
    private_token: 7389rz478
    state: absent


# add / update an ssh pubkey
- gitlab_user:
    username: test
    ssh_key_title: first_ssh_key
    ssh_key: lookup('file', '/some/path/id_rsa.pub')
    api_url: https://gitlab-url-internal.somedomain.com/api/v3
    private_token: 7389rz478
    state: present
'''

import ansible.module_utils.urls as urls
import urllib2

allowed_user_params = [
    'password', 'username', 'name', 'skype', 'linkedin', 'twitter', 'website_url', 'projects_limit',
    'extern_uid', 'provider', 'bio', 'can_create_group'
]
required_user_create_params = [
    'email', 'username', 'name', 'password'
]
required_user_update_params = [
    'username'
]


class GitlabModuleInternalException(Exception):
    pass


def _send_request(method, url, headers, body=None):
    try:
        response_reader = urls.open_url(
            url,
            method=method,
            headers=headers,
            data=body
        )

        response_headers = response_reader.headers
        response_body = response_reader.read()
        response_reader.close()
        return response_headers, response_body

    except urllib2.URLError as e:
        if 'message' in dir(e.reason):
            raise GitlabModuleInternalException(e.reason.message)
        raise GitlabModuleInternalException(e.reason + '\n' + e.read())


def _get_email_id(api_url, user_id, private_token, email):
    headers, body = _send_request('GET', '%s/users/%d/emails' % (api_url, user_id), {'PRIVATE-TOKEN': private_token})
    if headers['status'] != '200 OK':
        return None

    for tmp_email in json.loads(body):
        if tmp_email['email'] == email.lower():  # gitlab converts email addresses to lower case
            return tmp_email['id']

    return None


def _find_user_by_name(api_url, username, private_token):
    headers, body = _send_request(
        url=api_url + '/users',
        method='GET',
        headers={'PRIVATE-TOKEN': private_token}
    )

    try:
        content = json.loads(body)
        for user in content:
            if user['username'] == username:
                return user
    except:
        pass

    return None


def _get_ssh_key_for_user(api_url, private_token, user_id, ssh_key_title):
    response_headers, response_body = _send_request(
        'GET',
        '%s/users/%d/keys' % (api_url, user_id),
        {'PRIVATE-TOKEN': private_token}
    )

    if response_headers['status'] == '200 OK':
        available_keys = [key for key in json.loads(response_body) if key['title'] == ssh_key_title]
        if len(available_keys) > 0:
            return available_keys[0]

    return {}


def _add_non_standard_params(params, raw_data):
    """non standard params are parameters that are spelled differently in GET and POST/PUT requests
       For example 'admin' in POST/PUT requests is called 'is_admin' in GET
    """
    if 'admin' in params and params['admin'] is not None:
        raw_data['admin'] = params['admin']
    if 'email' in params and params['email'] is not None:
        raw_data['email'] = params['email']
    return raw_data


def _check_required_input_params(raw_data, user):
    required_params = required_user_create_params
    if user:
        required_params = required_user_update_params
    return len(required_params) == len([param_name for param_name in required_params if param_name in raw_data])


def _predict_user_change(raw_data, user):
    return not user or ('admin' in raw_data and 'is_admin' in user and raw_data['admin'] != user['is_admin']) or \
        0 < len([param_name
                 for param_name
                 in allowed_user_params
                 if (param_name in user and param_name in raw_data and user[param_name] != raw_data[param_name])
                 or (param_name not in user and param_name in raw_data)])


def _update_ssh_key(api_url, private_token, ssh_key_id, ssh_key_title, ssh_key, user_id):
    if ssh_key_id:
        _send_request(
            'DELETE',
            '%s/users/%d/keys/%d' % (api_url, user_id, ssh_key_id),
            {'PRIVATE-TOKEN': private_token}
        )
    ssh_response_headers, ssh_response_body = _send_request(
        'POST',
        '%s/users/%d/keys' % (api_url, user_id),
        {'PRIVATE-TOKEN': private_token, 'Content-Type': 'application/json'},
        json.dumps({'id': user_id, 'title': ssh_key_title, 'key': ssh_key})
    )
    if ssh_response_headers['status'] not in ('200 OK', '201 Created'):
        raise GitlabModuleInternalException('\n'.join((ssh_response_headers['status'], ssh_response_body)))


def _update_user(params, user, user_request_input):
    if user:  # update user
        url = '%s/users/%d' % (params['api_url'], user['id'])
        method = 'PUT'
        del user_request_input['email']  # email update is handled separately in _update_email
        # in fact: including email in user update requests has no effect
    else:  # create new user
        url = '%s/users' % params['api_url']
        method = 'POST'

    user_response_headers, user_response_body = _send_request(
        method,
        url,
        {'PRIVATE-TOKEN': params['private_token'], 'Content-Type': 'application/json'},
        json.dumps(user_request_input)
    )
    if user_response_headers['status'] in ('201 Created', '200 OK'):
        return json.loads(user_response_body)

    raise GitlabModuleInternalException('\n'.join((user_response_headers['status'], user_response_body)))


def _update_email(api_url, private_token, user_id, email_id, email):
    delete_response_headers, delete_response_body = _send_request(
        'DELETE',
        '%s/users/%d/emails/%d' % (api_url, user_id, email_id),
        {'PRIVATE-TOKEN': private_token}
    )
    if delete_response_headers['status'] != '200 OK':
        raise GitlabModuleInternalException('\n'.join((delete_response_headers['status'], delete_response_body)))

    create_response_header, create_response_body = _send_request(
        'POST',
        '%s/users/%d/emails' % (api_url, user_id),
        {'PRIVATE-TOKEN': private_token, 'Content-Type': 'application/json'},
        json.dumps({'id': user_id, 'email': email})
    )
    if create_response_header['status'] == '201 Created':
        return True
    
    raise GitlabModuleInternalException('\n'.join((create_response_header['status'], create_response_body)))


def remove_user(params, check_mode):
    user = _find_user_by_name(params['api_url'], params['username'], params['private_token'])

    change = bool(user)
    if check_mode or not change:
        return change

    headers, body = _send_request(
        url='%s/users/%d' % (params['api_url'], user['id']),
        method='DELETE',
        headers={'PRIVATE-TOKEN': params['private_token']}
    )

    if headers['status'] == '200 OK':
        return True

    raise GitlabModuleInternalException('\n'.join((headers['status'], body)))


def create_or_update_user(params, check_mode):
    user = _find_user_by_name(params['api_url'], params['username'], params['private_token'])
    if user and 'ssh_key_title' in params:
        ssh_key = _get_ssh_key_for_user(params['api_url'], params['private_token'], user['id'], params['ssh_key_title'])
    else:
        ssh_key = {}

    email_change = False
    if 'email' in params and user and user['email'] != params['email']:
        email_change = True

    user_request_input = {param_name: params[param_name]
                          for param_name
                          in allowed_user_params
                          if param_name in params and params[param_name] is not None}
    user_request_input = _add_non_standard_params(params, user_request_input)

    if not _check_required_input_params(user_request_input, user):
        raise GitlabModuleInternalException(
            ', '.join(required_user_create_params) + ' are required when creating a new user'
        )

    ssh_key_change = 'ssh_key' in params and ('key' not in ssh_key or ssh_key['key'] != params['ssh_key'])
    user_change = _predict_user_change(user_request_input, user)
    if check_mode or (not user_change and not ssh_key_change and not email_change):
        return user_change or ssh_key_change

    if user_change:
        user = _update_user(params, user, user_request_input)
    if user and ssh_key_change:
        _update_ssh_key(
            params['api_url'],
            params['private_token'],
            ssh_key['id'] if ssh_key and 'id' in ssh_key else None,
            params['ssh_key_title'],
            params['ssh_key'],
            user['id']
        )
    if email_change:
        _update_email(
            params['api_url'],
            params['private_token'],
            user['id'],
            _get_email_id(params['api_url'], user['id'], params['private_token'], user['email']),
            params['email']
        )

    return True


def main():
    global ansible_module
    ansible_module = AnsibleModule(
        argument_spec=dict(
            username=dict(required=True),
            private_token=dict(required=True, no_log=True),
            api_url=dict(required=True),
            name=dict(required=False, default=None),
            email=dict(required=False, default=None),
            password=dict(required=False, default=None, no_log=True),
            skype=dict(required=False, default=None),
            linkedin=dict(required=False, default=None),
            twitter=dict(required=False, default=None),
            website_url=dict(required=False, default=None),
            projects_limit=dict(required=False, default=None),
            extern_uid=dict(required=False, default=None),
            provider=dict(required=False, default=None),
            bio=dict(required=False, default=None),
            admin=dict(required=False, default=None, choices=BOOLEANS),
            can_create_group=dict(required=False, default=None, choices=BOOLEANS),
            ssh_key_title=dict(required=False, default=None),
            ssh_key=dict(required=None, default=None),
            state=dict(required=False, default='present', choices=['present', 'absent']),
        ),
        required_together=[['ssh_key_title', 'ssh_key']],
        supports_check_mode=True
    )

    if 'admin' in ansible_module.params:
        ansible_module.params['admin'] = ansible_module.boolean(ansible_module.params['admin'])
    if 'can_create_group' in ansible_module.params:
        ansible_module.params['can_create_group'] = ansible_module.boolean(ansible_module.params['can_create_group'])

    try:
        changed = False
        if ansible_module.params['state'] == 'absent':
            changed = remove_user(ansible_module.params, ansible_module.check_mode)
        elif ansible_module.params['state'] == 'present':
            changed = create_or_update_user(ansible_module.params, ansible_module.check_mode)
        ansible_module.exit_json(changed=changed)
    except GitlabModuleInternalException as e:
        ansible_module.fail_json(msg=e.message)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
