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
