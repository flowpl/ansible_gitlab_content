# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class GitlabUserGetEmailIdTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testAllOK(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, '[{"id":1,"email":"anything@tada.com"},{"id":2,"email":"someone@something.com"}]'
        result = library.gitlab_user._get_email_id('http://somedomain.com/api/v3', 1, '576932', 'someone@something.com')
        self.assertEqual(2, result)

    @mock.patch('library.gitlab_user._send_request')
    def testRequestFailed(self, send_request_mock):
        send_request_mock.return_value = {'status': '500 Internal Server Error'}, ''
        result = library.gitlab_user._get_email_id('http://somedomain.com/api/v3', 1, '576932', 'someone@something.com')
        self.assertIsNone(result)

    @mock.patch('library.gitlab_user._send_request')
    def testEmailNotFound(self, send_request_mock):
        send_request_mock.return_value = \
            {'status': '200 OK'}, '[{"id":1,"email":"anything@tada.com"}]'
        result = library.gitlab_user._get_email_id('http://somedomain.com/api/v3', 1, '576932', 'someone@something.com')
        self.assertIsNone(result)
