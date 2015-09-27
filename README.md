# Ansible Modules to manage Gitlab


## gitlab_user
creates, updates or deletes user accounts.

It uses the 'username' argument as the user identifier instead of the ansible standard 'name'
as Gitlab uses 'name' for a different meaning.

##### always required arguments

- username
- private_token
- api_url

##### arguments required on user create and optional on user update

- name
- email
- password

##### optional arguments

- skype
- linkedin
- twitter
- website_url
- projects_limit
- extern_uid
- provider
- bio
- admin
- can_create_group
- state

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