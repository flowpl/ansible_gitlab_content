# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user


class RemoveUserTest(unittest.TestCase):

    @mock.patch('library.gitlab_user._find_user_by_name')
    @mock.patch('library.gitlab_user._send_request')
    def testRemoveNonExistingUser(self, send_request_mock, find_user_mock):
        find_user_mock.return_value = None

        result = library.gitlab_user.remove_user(
            {'username': 'username', 'api_url': 'http://somedomain.com/api/v3', 'private_token': '576932'},
            False
        )
        self.assertFalse(result)

        self.assertEquals('http://somedomain.com/api/v3', find_user_mock.call_args_list[0][0][0])
        self.assertEquals('576932', find_user_mock.call_args_list[0][0][1])
        self.assertEquals('username', find_user_mock.call_args_list[0][0][2])

        self.assertEquals(0, send_request_mock.call_count)

    @mock.patch('library.gitlab_user._find_user_by_name')
    @mock.patch('library.gitlab_user._send_request')
    def testRemoveExistingUser(self, send_request_mock, find_user_mock):
        find_user_mock.return_value = {'id': 12}
        send_request_mock.return_value = {'status': '200 OK'}, ''

        result = library.gitlab_user.remove_user(
            {'username': 'username', 'api_url': 'http://somedomain.com/api/v3', 'private_token': '576932'},
            False
        )
        self.assertTrue(result)

        self.assertEquals('http://somedomain.com/api/v3', find_user_mock.call_args_list[0][0][0])
        self.assertEquals('576932', find_user_mock.call_args_list[0][0][1])
        self.assertEquals('username', find_user_mock.call_args_list[0][0][2])

        self.assertEquals('DELETE', send_request_mock.call_args_list[0][1]['method'])
        self.assertEquals('http://somedomain.com/api/v3/users/12', send_request_mock.call_args_list[0][1]['url'])
        self.assertEquals({'PRIVATE-TOKEN': '576932'}, send_request_mock.call_args_list[0][1]['headers'])

    @mock.patch('library.gitlab_user._find_user_by_name')
    @mock.patch('library.gitlab_user._send_request')
    def testGitlabApiRespondsWithError(self, send_request_mock, find_user_mock):
        find_user_mock.return_value = {'id': 12}
        send_request_mock.return_value = {'status': '500 Internal Server Error'}, 'some message'

        with self.assertRaises(library.gitlab_user.GitlabModuleInternalException) as ex:
            library.gitlab_user.remove_user(
                {'username': 'username', 'api_url': 'http://somedomain.com/api/v3', 'private_token': '576932'},
                False
            )
        self.assertEqual('500 Internal Server Error\nsome message', ex.exception.message)