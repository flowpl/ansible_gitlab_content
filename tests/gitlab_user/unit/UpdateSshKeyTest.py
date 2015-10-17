# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class UpdateSshKeyTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._send_request')
    def testCreateNewSshKey(self, send_request_mock):
        send_request_mock.return_value = {'status': '201 Created'}, ''

        library.gitlab_user._update_ssh_key(
            'http://somedomain.com/api/v3',
            '576932',
            12,
            None,
            'title',
            'hishguislg'
        )

        self.assertEquals('POST', send_request_mock.call_args_list[0][0][0])
        self.assertEquals(
            'http://somedomain.com/api/v3/users/12/keys',
            send_request_mock.call_args_list[0][0][1]
        )
        self.assertEquals(
            {'PRIVATE-TOKEN': '576932', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[0][0][2]
        )
        self.assertEquals(
            '{"id": 12, "key": "hishguislg", "title": "title"}',
            send_request_mock.call_args_list[0][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testUpdateExistingSshKey(self, send_request_mock):
        send_request_mock.return_value = {'status': '201 Created'}, ''

        library.gitlab_user._update_ssh_key(
            'http://somedomain.com/api/v3',
            '576932',
            12,
            1,
            'title',
            'hishguislg'
        )

        self.assertEquals('DELETE', send_request_mock.call_args_list[0][0][0])
        self.assertEquals('http://somedomain.com/api/v3/users/12/keys/1', send_request_mock.call_args_list[0][0][1])
        self.assertEquals({'PRIVATE-TOKEN': '576932'}, send_request_mock.call_args_list[0][0][2])

        self.assertEquals('POST', send_request_mock.call_args_list[1][0][0])
        self.assertEquals(
            'http://somedomain.com/api/v3/users/12/keys',
            send_request_mock.call_args_list[1][0][1]
        )
        self.assertEquals(
            {'PRIVATE-TOKEN': '576932', 'Content-Type': 'application/json'},
            send_request_mock.call_args_list[1][0][2]
        )
        self.assertEquals(
            '{"id": 12, "key": "hishguislg", "title": "title"}',
            send_request_mock.call_args_list[1][0][3]
        )

    @mock.patch('library.gitlab_user._send_request')
    def testGitlabApiRespondsWithError(self, send_request_mock):
        send_request_mock.return_value = {'status': '500 Internal Server Error'}, 'some message'

        with self.assertRaises(library.gitlab_user.GitlabModuleInternalException) as ex:
            library.gitlab_user._update_ssh_key(
                'http://somedomain.com/api/v3',
                '576932',
                12,
                None,
                'title',
                'hishguislg'
            )
        self.assertEquals("500 Internal Server Error\nsome message", ex.exception.message)
