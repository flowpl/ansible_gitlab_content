# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class UpdateUserTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifUserIsNotChangedAndPasswordNotGiven_dontSendUpdateRequest(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, \
            '[{"username":"testusername", "name": "Test", "email":"someone@something.com"}]'
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertFalse(result)
        self.assertEquals(1, send_request_mock.call_count)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifUserIsNotChangedAndPasswordNotGivenAndCheckMode_dontSendUpdateRequest(
            self,
            send_request_mock):

        send_request_mock.return_value = \
            {'status': '200 OK'}, \
            '[{"username":"testusername", "name": "Test", "email":"someone@something.com"}]'
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertFalse(result)
        self.assertEquals(1, send_request_mock.call_count)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifUserIsNotChangedAndPasswordGiven_sendUpdateRequest(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'),
            ({'status': '200 OK'}, '{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '9876abc123',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(2, send_request_mock.call_count)

        self.assert_get_users_request(send_request_mock)

        self.assertEquals('PUT', send_request_mock.call_args_list[1][0][0])
        self.assertEquals(
            {'PRIVATE-TOKEN': 'abc123', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[1][0][2]
        )
        self.assertEquals('http://something.com/api/v3/users/12', send_request_mock.call_args_list[1][0][1])
        self.assertEquals(
            '{"username": "testusername", "password": "9876abc123", "email": "someone@something.com", "name": "Test"}',
            send_request_mock.call_args_list[1][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifUserIsNotChangedAndPasswordGivenAndCheckMode_sendUpdateRequest(
            self,
            send_request_mock):

        send_request_mock.return_value = \
            {'status': '200 OK'}, \
            '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'

        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '9876abc123',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertTrue(result)
        self.assertEquals(1, send_request_mock.call_count)

        self.assert_get_users_request(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifUserIsChangedOtherThanPassword_sendUpdateRequest(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'},
             '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'),
            ({'status': '200 OK'},
             '{"username":"testusername","id":12,"name":"someOtherName","email":"someone@something.com"}')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'someOtherName',
                'email': 'someone@something.com',
                'password': '9876abc123',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(2, send_request_mock.call_count)

        self.assert_get_users_request(send_request_mock)

        self.assertEquals('PUT', send_request_mock.call_args_list[1][0][0])
        self.assertEquals(
            {'PRIVATE-TOKEN': 'abc123', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[1][0][2]
        )
        self.assertEquals('http://something.com/api/v3/users/12', send_request_mock.call_args_list[1][0][1])
        self.assertEquals(
            '{"username": "testusername", "password": "9876abc123", "email": "someone@something.com", "name": "someOtherName"}',
            send_request_mock.call_args_list[1][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifUserIsChangedOtherThanPasswordAndCheckMode_dontSendUpdateRequest(
            self,
            send_request_mock):

        send_request_mock.return_value = \
            {'status': '200 OK'}, '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'

        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'someOtherName',
                'email': 'someone@something.com',
                'password': '9876abc123',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertTrue(result)
        self.assertEquals(1, send_request_mock.call_count)

        self.assert_get_users_request(send_request_mock)

    @mock.patch('library.gitlab_user.ansible_module')
    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifAdminIsChanged_sendUpdateRequest(self, send_request_mock, ansible_module):

        ansible_module.boolean = mock.MagicMock()
        ansible_module.boolean.return_value = False

        send_request_mock.side_effect = (
            ({'status': '200 OK'},
             '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com","is_admin":true}]'),
            ({'status': '200 OK'},
             '{"username":"testusername","id":12,"name":"someOtherName","email":"someone@something.com"}')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'someOtherName',
                'email': 'someone@something.com',
                'admin': 'false',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(2, send_request_mock.call_count)

        self.assert_get_users_request(send_request_mock)

        self.assertEquals('PUT', send_request_mock.call_args_list[1][0][0])
        self.assertEquals(
            {'PRIVATE-TOKEN': 'abc123', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[1][0][2]
        )
        self.assertEquals('http://something.com/api/v3/users/12', send_request_mock.call_args_list[1][0][1])
        self.assertEquals(
            '{"username": "testusername", "admin": false, "email": "someone@something.com", "name": "someOtherName"}',
            send_request_mock.call_args_list[1][0][3]
        )

    def assert_get_users_request(self, send_request_mock):
        self.assertEquals('GET', send_request_mock.call_args_list[0][1]['method'])
        self.assertEquals({'PRIVATE-TOKEN': 'abc123'}, send_request_mock.call_args_list[0][1]['headers'])
        self.assertEquals('http://something.com/api/v3/users', send_request_mock.call_args_list[0][1]['url'])
