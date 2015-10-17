# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class UpdateUserTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testCreateNewUser(self, send_request_mock):
        send_request_mock.return_value = {'status': '201 Created'}, '{"id":12,"name":"name"}'

        result = library.gitlab_user._update_user(
            'http://somedomain.com/api/v3',
            '576932',
            None,
            {'name': 'name', 'username': 'username', 'password': 'password', 'email': 'email'}
        )

        self.assertEquals('POST', send_request_mock.call_args_list[0][0][0])
        self.assertEquals('http://somedomain.com/api/v3/users', send_request_mock.call_args_list[0][0][1])
        self.assertEquals(
            {'PRIVATE-TOKEN': '576932', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[0][0][2]
        )
        self.assertEquals(
            '{"username": "username", "password": "password", "name": "name", "email": "email"}',
            send_request_mock.call_args_list[0][0][3]
        )

        self.assertEquals({'id': 12, 'name': 'name'}, result)

    @mock.patch('library.gitlab_user._send_request')
    def testUpdateExistingUser(self, send_request_mock):
        send_request_mock.return_value = {'status': '200 OK'}, '{"id":12,"name":"name"}'

        result = library.gitlab_user._update_user(
            'http://somedomain.com/api/v3',
            '576932',
            12,
            {'name': 'name', 'username': 'username', 'password': 'password', 'email': 'email'}
        )

        self.assertEquals('PUT', send_request_mock.call_args_list[0][0][0])
        self.assertEquals('http://somedomain.com/api/v3/users/12', send_request_mock.call_args_list[0][0][1])
        self.assertEquals(
            {'PRIVATE-TOKEN': '576932', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[0][0][2]
        )
        self.assertEquals(
            '{"password": "password", "name": "name"}',
            send_request_mock.call_args_list[0][0][3]
        )

        self.assertEqual({'id': 12, 'name': 'name'}, result)

    @mock.patch('library.gitlab_user._send_request')
    def testGitlabApiRespondsWithError(self, send_request_mock):
        send_request_mock.return_value = {'status': '500 Internal Server Error'}, 'some message'

        with self.assertRaises(library.gitlab_user.GitlabModuleInternalException) as ex:
            library.gitlab_user._update_user(
                'http://somedomain.com/api/v3',
                '576932',
                12,
                {'name': 'name', 'username': 'username', 'password': 'password', 'email': 'email'}
            )
        self.assertEqual('500 Internal Server Error\nsome message', ex.exception.message)


