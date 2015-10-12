# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class GetSshKeyForUserTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testAllOK(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, \
            '[{"id":1,"title":"key4","key":"vireaofhudsagfrio"},{"id":14,"title":"key1","key":"nvireqvtgzoufigru"}]'
        result = library.gitlab_user._get_ssh_key_for_user('http://somedomain.com/api/v3', '576932', 12, 'key1')
        self.assertEqual({"id": 14, "title": "key1", "key": "nvireqvtgzoufigru"}, result)
        self.assert_send_request_call(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testRequestFailed(self, send_request_mock):
        send_request_mock.return_value = {'status': '500 Internal Server Error'}, ''
        result = library.gitlab_user._get_ssh_key_for_user('http://somedomain.com/api/v3', '576932', 12, 'key1')
        self.assertEqual({}, result)
        self.assert_send_request_call(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testKeyNotFound(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, \
            '[{"id":1,"title":"key4","key":"vireaofhudsagfrio"}]'
        result = library.gitlab_user._get_ssh_key_for_user('http://somedomain.com/api/v3', '576932', 12, 'key1')
        self.assertEqual({}, result)
        self.assert_send_request_call(send_request_mock)

    def assert_send_request_call(self, send_request_mock):
        self.assertEquals('GET', send_request_mock.call_args_list[0][0][0])
        self.assertEquals('http://somedomain.com/api/v3/users/12/keys', send_request_mock.call_args_list[0][0][1])
        self.assertEquals({'PRIVATE-TOKEN': '576932'}, send_request_mock.call_args_list[0][0][2])