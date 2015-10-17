# -*- encoding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class FindUserByNameTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testAllOK(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, \
            '[{"username":"someone","id":3,"name":"Test","email":"anyone@something.com"},{"username":"testusername","id":12,"name":"Test","email":"someone@something.com"}]'
        result = library.gitlab_user._find_user_by_name('http://somedomain.com/api/v3', '576932', 'testusername')
        self.assertEqual(
            {"username": "testusername", "id": 12, "name": "Test", "email": "someone@something.com"},
            result
        )
        self.assert_send_request_call(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testRequestFailed(self, send_request_mock):
        send_request_mock.return_value = {'status': '500 Internal Server Error'}, ''
        result = library.gitlab_user._find_user_by_name('http://somedomain.com/api/v3', '576932', 'testusername')
        self.assertIsNone(result)
        self.assert_send_request_call(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testUserNotFound(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, \
            '[{"username":"someone","id":3,"name":"Test","email":"anyone@something.com"}]'
        result = library.gitlab_user._find_user_by_name('http://somedomain.com/api/v3', '576932', 'testusername')
        self.assertIsNone(result)
        self.assert_send_request_call(send_request_mock)

    def assert_send_request_call(self, send_request_mock):
        self.assertEquals('GET', send_request_mock.call_args_list[0][1]['method'])
        self.assertEquals('http://somedomain.com/api/v3/users', send_request_mock.call_args_list[0][1]['url'])
        self.assertEquals({'PRIVATE-TOKEN': '576932'}, send_request_mock.call_args_list[0][1]['headers'])
