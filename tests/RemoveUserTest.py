# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class RemoveUserTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testDeleteUser_ifNoneExists_dontSendDeleteRequest(self, send_request_mock):
        send_request_mock.return_value = {'status': '200 OK'}, '[]'
        result = library.gitlab_user.remove_user({
                'username': 'testusername',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertFalse(result)
        self.assertEquals(1, send_request_mock.call_count)

    @mock.patch('library.gitlab_user._send_request')
    def testDeleteUser_ifExists_sendDeleteRequest(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, '[{"username":"testusername","id":12}]'),
            ({'status': '200 OK'}, '')
        )
        result = library.gitlab_user.remove_user({
                'username': 'testusername',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            False
        )
        self.assertTrue(result)
        self.assertEquals(2, send_request_mock.call_count)

    @mock.patch('library.gitlab_user._send_request')
    def testDeleteUser_ifNoneExistsAndCheckMode_dontSendDeleteRequest(self, send_request_mock):
        send_request_mock.return_value = {'status': '200 OK'}, '[]'
        result = library.gitlab_user.remove_user({
                'username': 'testusername',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertFalse(result)
        self.assertEquals(1, send_request_mock.call_count)

    @mock.patch('library.gitlab_user._send_request')
    def testDeleteUser_ifExistsAndCheckMode_dontSendDeleteRequest(self, send_request_mock):
        send_request_mock.return_value = {'status': '200 OK'}, '[{"username":"testusername","id":12}]',
        result = library.gitlab_user.remove_user({
                'username': 'testusername',
                'api_url': 'http://something.com/api/v3',
                'private_token': 'abc123'
            },
            True
        )
        self.assertTrue(result)
        self.assertEquals(1, send_request_mock.call_count)
