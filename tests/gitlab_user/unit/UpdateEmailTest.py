# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class UpdateEmailTest(unittest.TestCase):
    """creating a new email cannot happen as email is required in user create requests"""

    @mock.patch('library.gitlab_user._send_request')
    def testUpdateExistingEmail(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, ''),
            ({'status': '201 Created'}, '')
        )

        library.gitlab_user._update_email(
            'http://somedomain.com/api/v3',
            '576932',
            12,
            1,
            'someone@something.com'
        )

        self.assertEquals('DELETE', send_request_mock.call_args_list[0][0][0])
        self.assertEquals('http://somedomain.com/api/v3/users/12/emails/1', send_request_mock.call_args_list[0][0][1])
        self.assertEquals({'PRIVATE-TOKEN': '576932'}, send_request_mock.call_args_list[0][0][2])

        self.assertEquals('POST', send_request_mock.call_args_list[1][0][0])
        self.assertEquals(
            'http://somedomain.com/api/v3/users/12/emails',
            send_request_mock.call_args_list[1][0][1]
        )
        self.assertEquals(
            {'PRIVATE-TOKEN': '576932', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[1][0][2]
        )
        self.assertEquals(
            '{"id": 12, "email": "someone@something.com"}',
            send_request_mock.call_args_list[1][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testGitlabApiRespondsWithErrorOnDelete(self, send_request_mock):
        send_request_mock.return_value = {'status': '500 Internal Server Error'}, 'some message'

        with self.assertRaises(library.gitlab_user.GitlabModuleInternalException) as ex:
            library.gitlab_user._update_email(
                'http://somedomain.com/api/v3',
                '576932',
                12,
                None,
                'someone@something.com'
            )
        self.assertEquals("500 Internal Server Error\nsome message", ex.exception.message)

    @mock.patch('library.gitlab_user._send_request')
    def testGitlabApiRespondsWithErrorOnDelete(self, send_request_mock):
        send_request_mock.side_effect = (
            ({'status': '200 OK'}, ''),
            ({'status': '500 Internal Server Error'}, 'some message')
        )

        with self.assertRaises(library.gitlab_user.GitlabModuleInternalException) as ex:
            library.gitlab_user._update_email(
                'http://somedomain.com/api/v3',
                '576932',
                12,
                1,
                'someone@something.com'
            )
        self.assertEquals("500 Internal Server Error\nsome message", ex.exception.message)