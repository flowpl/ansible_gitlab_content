# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class GetEmailIdTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testAllOK(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, '[{"id":1,"email":"anything@tada.com"},{"id":2,"email":"someone@something.com"}]'
        result = library.gitlab_user._get_email_id('http://somedomain.com/api/v3', '576932', 1, 'someone@something.com')
        self.assertEqual(2, result)
        self.assert_send_request_call(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testRequestFailed(self, send_request_mock):
        send_request_mock.return_value = {'status': '500 Internal Server Error'}, ''
        result = library.gitlab_user._get_email_id('http://somedomain.com/api/v3', '576932', 1, 'someone@something.com')
        self.assertIsNone(result)
        self.assert_send_request_call(send_request_mock)

    @mock.patch('library.gitlab_user._send_request')
    def testEmailNotFound(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, '[{"id":1,"email":"anything@tada.com"}]'
        result = library.gitlab_user._get_email_id('http://somedomain.com/api/v3', '576932', 1, 'someone@something.com')
        self.assertIsNone(result)
        self.assert_send_request_call(send_request_mock)

    def assert_send_request_call(self, send_request_mock):
        self.assertEqual('http://somedomain.com/api/v3/users/1/emails', send_request_mock.call_args_list[0][0][1])
        self.assertEqual({'PRIVATE-TOKEN': '576932'}, send_request_mock.call_args_list[0][0][2])
        self.assertEqual('GET', send_request_mock.call_args_list[0][0][0])
