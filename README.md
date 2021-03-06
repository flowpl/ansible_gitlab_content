# Ansible Modules to manage Gitlab Content

A collection of ansible modules to add content to a running gitlab installation via it's REST API.

![Travis build status](https://travis-ci.org/flowpl/ansible_gitlab_content.svg?branch=master)
![Coverage Status](https://coveralls.io/repos/flowpl/ansible_gitlab_content/badge.svg?branch=master&service=github)

## gitlab_user
creates, updates or deletes user accounts.

The module supports only one email address and one ssh pubkey per user account. See gitlab_email and gitlab_pubkey if you need more.

It uses the 'username' argument as the user identifier instead of the ansible standard 'name'
as Gitlab uses 'name' for a different meaning.

see library/gitlab_user.py for parameter documentation

##### examples

```YAML
- name: ensure user is present
  gitlab_user:
    username: test
    password: abc123yz
    name: some name
    email: someone@something.com
    api_url: https://gitlab-url-internal.somedomain.com/api/v3
    private_token: 7389rz478
    state: present
```

```YAML
# change a user's email
# this only works if the user already exists because of the missing password and name
- name: ensure user is present
  gitlab_user:
    username: test
    email: someone_else@something.com
    api_url: https://gitlab-url-internal.somedomain.com/api/v3
    private_token: 7389rz478
    state: present
```

```YAML
# delete a user
- name: ensure user is present
  gitlab_user:
    username: test
    api_url: https://gitlab-url-internal.somedomain.com/api/v3
    private_token: 7389rz478
    state: absent
```

```YAML
# add / update an ssh pubkey
- gitlab_user:
    username: test
    ssh_key_title: first_ssh_key
    ssh_key: lookup('file', '/some/path/id_rsa.pub')
    api_url: https://gitlab-url-internal.somedomain.com/api/v3
    private_token: 7389rz478
    state: present
```