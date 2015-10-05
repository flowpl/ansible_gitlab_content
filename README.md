# Ansible Modules to manage Gitlab


## gitlab_user
creates, updates or deletes user accounts.

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