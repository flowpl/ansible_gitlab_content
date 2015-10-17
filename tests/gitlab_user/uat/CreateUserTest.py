# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user
import ddt


@ddt.ddt
class CreateUserTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExists_sendCreateRequest(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, '[{"username":"someuser"}]'),
            ({'status': '201 Created'}, '{"username":"testusername","id":12}')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExistsAndCheckMode_dontSendRequest(self, send_request_mock):
        send_request_mock.return_value = {'status': '200 OK'}, '[{"username":"someuser"}]'
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertTrue(result)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExistsAndSshKeyGiven_sendCreateUserAndAddSshKeyRequests(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, '[{"username":"someuser"}]'),
            ({'status': '201 Created'}, '{"username":"testusername","id":12}'),
            ({'status': '201 Created'}, '{"id":1,"key":"ghkjfasdkjadh","title":"sometitle"}')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'ssh_key_title': 'sometitle',
                'ssh_key': 'ghkjfasdkjadh',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExistsAndSshKeyGivenAndCheckMode_dontSendCreateRequests(
            self,
            send_request_mock):

        send_request_mock.return_value = {'status': '200 OK'}, '[{"username":"someuser"}]'
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'ssh_key_title': 'sometitle',
                'ssh_key': 'ghkjfasdkjadh',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertTrue(result)

    @ddt.data(
        {'username': 'testusername', 'name': 'Test', 'password': '98765btzf'},
        {'username': 'testusername', 'email': 'someone@something.com', 'password': '98765btzf'},
        {'username': 'testusername', 'name': 'Test', 'email': 'someone@something.com'}
    )
    def testCreateOrUpdateUser_ifRequiredArgumentIsMissing_throwExceptionDontSendRequest(self, input_arguments):
        with mock.patch('library.gitlab_user._send_request') as send_request_mock:
            send_request_mock.return_value = {'status': '200 OK'}, '[{"username":"someuser"}]'
            arguments = {'api_url': 'http://something.com/api/v3', 'private_token': 'abc123'}
            arguments.update(input_arguments)
            with self.assertRaises(library.gitlab_user.GitlabModuleInternalException):
                library.gitlab_user.create_or_update_user(arguments, False)

    @ddt.data(
        {'username': 'testusername', 'name': 'Test', 'password': '98765btzf'},
        {'username': 'testusername', 'email': 'someone@something.com', 'password': '98765btzf'},
        {'username': 'testusername', 'name': 'Test', 'email': 'someone@something.com'}
    )
    def testCreateOrUpdateUser_ifRequiredArgumentIsMissingAndCheckMode_throwExceptionDontSendRequest(
            self, input_arguments):

        with mock.patch('library.gitlab_user._send_request') as send_request_mock:
            send_request_mock.return_value = {'status': '200 OK'}, '[{"username":"someuser"}]'
            arguments = {'api_url': 'http://something.com/api/v3', 'private_token': 'abc123'}
            arguments.update(input_arguments)
            with self.assertRaises(library.gitlab_user.GitlabModuleInternalException):
                library.gitlab_user.create_or_update_user(arguments, True)

    @mock.patch('library.gitlab_user._send_request')
    def testCreateOrUpdateUser_ifNoneExistsAndAdminGiven_sendCreateUserRequests(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, '[{"username":"someuser"}]'),
            ({'status': '201 Created'}, '{"username":"testusername","id":12,"is_admin":true}')
        )
        result = library.gitlab_user.create_or_update_user(
            {
                'username': 'testusername',
                'name': 'Test',
                'email': 'someone@something.com',
                'password': '98765btzf',
                'admin': True,
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
