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
            ({'status': '200 OK'},
             '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'),
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
            '{"password": "9876abc123", "name": "Test"}',
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
            '{"password": "9876abc123", "name": "someOtherName"}',
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

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifAdminIsChanged_sendUpdateRequest(self, send_request_mock):
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
                'admin': False,
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
            '{"admin": false, "name": "someOtherName"}',
            send_request_mock.call_args_list[1][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifSshKeyGivenAndNoChange_dontSendAnyUpdateRequest(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'},
             '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'),
            ({'status': '200 OK'}, '[{"id":1,"title":"key1","key":"nvireqvtgzoufigru"}]')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'ssh_key_title': 'key1',
                'ssh_key': 'nvireqvtgzoufigru',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertFalse(result)
        self.assertEquals(2, send_request_mock.call_count)
        self.assert_get_users_request(send_request_mock)
        self.assert_get_ssh_keys_request(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifSshKeyGivenAndKeyChanged_deleteKeyAndCreateNew(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'},
             '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'),
            ({'status': '200 OK'}, '[{"id":1,"title":"key1","key":"nvireqvtgzoufigru"}]'),
            ({'status': '200 OK'}, ''),
            ({'status': '201 Created'}, '')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'ssh_key_title': 'key1',
                'ssh_key': '0987656782356',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(4, send_request_mock.call_count)
        self.assert_get_users_request(send_request_mock)
        self.assert_get_ssh_keys_request(send_request_mock)

        self.assertEqual('DELETE', send_request_mock.call_args_list[2][0][0])
        self.assertEqual({'PRIVATE-TOKEN': 'abc123'}, send_request_mock.call_args_list[2][0][2])
        self.assertEqual('http://something.com/api/v3/users/12/keys/1', send_request_mock.call_args_list[2][0][1])

        self.assertEqual('POST', send_request_mock.call_args_list[3][0][0])
        self.assertEqual(
            {'PRIVATE-TOKEN': 'abc123', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[3][0][2]
        )
        self.assertEqual('http://something.com/api/v3/users/12/keys', send_request_mock.call_args_list[3][0][1])
        self.assertEqual(
            '{"id": 12, "key": "0987656782356", "title": "key1"}',
            send_request_mock.call_args_list[3][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNewSshKeyGiven_sendKeyRequest(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'},
             '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'),
            ({'status': '200 OK'}, '[{"id":1,"title":"key1","key":"nvireqvtgzoufigru"}]'),
            ({'status': '201 Created'}, '')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'ssh_key_title': 'key2',
                'ssh_key': '0987656782356',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(3, send_request_mock.call_count)
        self.assert_get_users_request(send_request_mock)
        self.assert_get_ssh_keys_request(send_request_mock)

        self.assertEqual('POST', send_request_mock.call_args_list[2][0][0])
        self.assertEqual(
            {'PRIVATE-TOKEN': 'abc123', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[2][0][2]
        )
        self.assertEqual('http://something.com/api/v3/users/12/keys', send_request_mock.call_args_list[2][0][1])
        self.assertEqual(
            '{"id": 12, "key": "0987656782356", "title": "key2"}',
            send_request_mock.call_args_list[2][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifEmailGivenAndChanged_deleteEmailFromUserResponseAndSendNew(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'},
             '[{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'),
            ({'status': '200 OK'}, '[{"id":1,"email":"someone@something.com"}]'),
            ({'status': '200 OK'}, ''),
            ({'status': '201 Created'}, '')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someoneelse@somethingelse.net',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(4, send_request_mock.call_count)
        self.assert_get_users_request(send_request_mock)

        self.assertEqual('GET', send_request_mock.call_args_list[1][0][0])
        self.assertEqual({'PRIVATE-TOKEN': 'abc123'}, send_request_mock.call_args_list[1][0][2])
        self.assertEqual('http://something.com/api/v3/users/12/emails', send_request_mock.call_args_list[1][0][1])

        self.assertEqual('DELETE', send_request_mock.call_args_list[2][0][0])
        self.assertEqual({'PRIVATE-TOKEN': 'abc123'}, send_request_mock.call_args_list[2][0][2])
        self.assertEqual('http://something.com/api/v3/users/12/emails/1', send_request_mock.call_args_list[2][0][1])

        self.assertEqual('POST', send_request_mock.call_args_list[3][0][0])
        self.assertEqual(
            {'PRIVATE-TOKEN': 'abc123', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[3][0][2]
        )
        self.assertEqual('http://something.com/api/v3/users/12/emails', send_request_mock.call_args_list[3][0][1])
        self.assertEqual(
            '{"id": 12, "email": "someoneelse@somethingelse.net"}',
            send_request_mock.call_args_list[3][0][3]
        )

    def assert_get_ssh_keys_request(self, send_request_mock):
        self.assertEquals('GET', send_request_mock.call_args_list[1][0][0])
        self.assertEquals({'PRIVATE-TOKEN': 'abc123'}, send_request_mock.call_args_list[1][0][2])
        self.assertEquals('http://something.com/api/v3/users/12/keys', send_request_mock.call_args_list[1][0][1])

    def assert_get_users_request(self, send_request_mock):
        self.assertEquals('GET', send_request_mock.call_args_list[0][1]['method'])
        self.assertEquals({'PRIVATE-TOKEN': 'abc123'}, send_request_mock.call_args_list[0][1]['headers'])
        self.assertEquals('http://something.com/api/v3/users', send_request_mock.call_args_list[0][1]['url'])
