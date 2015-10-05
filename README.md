# Ansible Modules to manage Gitlab


## gitlab_user
creates, updates or deletes user accounts.

It uses the 'username' argument as the user identifier instead of the ansible standard 'name'
as Gitlab uses 'name' for a different meaning.

##### arguments


> username

required: always

the name used to identify a gitlab user. The gitlab_user module uses this as the user
identifier instead of the ansible default 'name' as 'name' has a different meaning in Gitlab

> private_token

the private token used for api authentication
required: always

> api_url

the URL fo the Gitlab API. e.g. http://gitlab-internal.somedomain.com/api/v3
required: always

> name
email
password
skype
linkedin
twitter
website_url
projects_limit
extern_uid
bio
admin
can_create_group
state
ssh_key_title
ssh_key

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