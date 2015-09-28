#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ansible.module_utils.urls as urls
import urllib2

allowed_user_params = [
    'email', 'password', 'username', 'name', 'skype', 'linkedin', 'twitter', 'website_url', 'projects_limit',
    'extern_uid', 'provider', 'bio', 'can_create_group'
]
required_user_create_params = [
    'email', 'username', 'name', 'password'
]
required_user_update_params = [
    'username'
]
ansible_module = None


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


def _find_user_by_name(api_url, username, private_token):
    headers, body = _send_request(
        url=api_url + '/users',
        method='GET',
        headers={'PRIVATE-TOKEN': private_token}
    )

    if headers['status'] != '200 OK':
        return None

    content = json.loads(body)
    for user in content:
        if user['username'] == username:
            return user
    return None


def _get_ssh_key_for_user(api_url, private_token, user_id, ssh_key_title):
    response_headers, response_body = _send_request(
        'GET',
        '%s/users/%d/keys' % (api_url, user_id),
        {'PRIVATE-TOKEN': private_token}
    )

    if response_headers['status'] == '200 OK':
        available_keys = [key for key in json.loads(response_body) if key['id'] == ssh_key_title]
        if len(available_keys) > 0:
            return available_keys[0]

    return None


def _create_user_request_method_and_url(api_url, user):
    if user:  # update user
        url = '%s/users/%d' % (api_url, user['id'])
        method = 'PUT'
    else:  # create new user
        url = '%s/users' % api_url
        method = 'POST'
    return method, url


def _add_non_standard_params(params, raw_data):
    '''non standard params are parameters that are spelled differently in GET and POST/PUT requests
       For example 'admin' in POST/PUT requests is called 'is_admin' in GET
    '''
    if 'admin' in params and params['admin'] is not None:
        raw_data['admin'] = params['admin']
    return raw_data


def _check_required_input_params(raw_data, user):
    required_params = required_user_create_params
    if user:
        required_params = required_user_update_params
    return len(required_params) == len([param_name for param_name in required_params if param_name in raw_data])


def _convert_request_input_values(raw_data):
    '''ansible accepts all kinds of values as booleans. Gitlab converts email to lower case.'''
    if 'admin' in raw_data:
        raw_data['admin'] = ansible_module.boolean(raw_data['admin'])
    if 'can_create_group' in raw_data:
        raw_data['can_create_group'] = ansible_module.boolean(raw_data['can_create_group'])
    if 'email' in raw_data:
        raw_data['email'] = raw_data['email'].lower()
    return raw_data


def _predict_user_change(raw_data, user):
    return not user or ('admin' in raw_data and 'is_admin' in user and raw_data['admin'] != user['is_admin']) or \
        0 < len([param_name
                 for param_name
                 in allowed_user_params
                 if (param_name in user and param_name in raw_data and user[param_name] != raw_data[param_name])
                 or (param_name not in user and param_name in raw_data)])


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

    user_request_input = {param_name: params[param_name]
                          for param_name
                          in allowed_user_params
                          if param_name in params and params[param_name] is not None}
    user_request_input = _add_non_standard_params(params, user_request_input)
    user_request_input = _convert_request_input_values(user_request_input)

    if not _check_required_input_params(user_request_input, user):
        raise GitlabModuleInternalException(
            ', '.join(required_user_create_params) + ' are required when creating a new user'
        )

    ssh_key_change = 'ssh_key' in params and ('key' not in ssh_key or ssh_key['key'] != params['ssh_key'])
    user_change = _predict_user_change(user_request_input, user)
    if check_mode or (not user_change and not ssh_key_change):
        # ---------------------------------------------------------------------------- no change exit
        return user_change or ssh_key_change

    user_method, user_url = _create_user_request_method_and_url(params['api_url'], user)
    user_response_headers, user_response_body = _send_request(
        user_method,
        user_url,
        {'PRIVATE-TOKEN': params['private_token'], 'Content-Type': 'application/json'},
        json.dumps(user_request_input)
    )
    if user_response_headers['status'] in ('201 Created', '200 OK'):
        user_exists = True
        user = json.loads()
    else:
        # ---------------------------------------------------------------------------- user create/update failed exit
        raise GitlabModuleInternalException('\n'.join((user_response_headers['status'], user_response_body)))

    if user_exists and ssh_key_change:
        ssh_response_headers, ssh_response_body = _send_request(
            'POST',
            '%s/users/%d/keys' % (params['api_url'], user['id']),
            {'PRIVATE-TOKEN': params['private_token'], 'Content-Type': 'application/json'},
            json.dumps({'id': user['id'], 'title': params['ssh_key_title'], 'key': params['ssh_key']})
        )
        if ssh_response_headers not in ('200 OK', '201 Created'):
            # ----------------------------------------------------------------------- ssh key create/update failed exit
            raise GitlabModuleInternalException('\n'.join((ssh_response_headers['status'], ssh_response_body)))

    # ------------------------------------------------------------------------------- all OK exit
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
