# -*- coding: utf-8 -*-

import unittest
import mock
import library.gitlab_user
import urllib2


class GitlabUserSendRequestTest(unittest.TestCase):

    @mock.patch('ansible.module_utils.urls.open_url')
    def testAllOk(self, open_url_mock):
        open_url_mock.return_value = mock.MagicMock()
        open_url_mock.return_value.headers = {'status': '200 OK'}
        open_url_mock.return_value.read = mock.MagicMock()
        open_url_mock.return_value.read.return_value = 'some message'
        open_url_mock.return_value.close = mock.MagicMock()

        result = library.gitlab_user._send_request(
            'GET',
            'http://something.com',
            {'Content-Type': 'text/csv'},
            'something'
        )

        self.assertEqual(result, ({'status': '200 OK'}, 'some message'))
        self.assertEqual('http://something.com', open_url_mock.call_args_list[0][0][0])
        self.assertEqual('something', open_url_mock.call_args_list[0][1]['data'])
        self.assertEqual({'Content-Type': 'text/csv'}, open_url_mock.call_args_list[0][1]['headers'])
        self.assertEqual('GET', open_url_mock.call_args_list[0][1]['method'])

    @mock.patch('ansible.module_utils.urls.open_url')
    def testRequestFailedWithReadableException(self, open_url_mock):
        error = urllib2.URLError('GitlabUserSendRequestTest.testRequestFailedWithReadableException')
        error.read = mock.MagicMock()
        error.read.return_value = 'some message'
        open_url_mock.side_effect = error

        with self.assertRaises(library.gitlab_user.GitlabModuleInternalException) as ex:
            library.gitlab_user._send_request(
                'GET',
                'http://something.com',
                {'Content-Type': 'text/csv'},
                'something'
            )

        self.assertEqual('GitlabUserSendRequestTest.testRequestFailedWithReadableException\nsome message', ex.exception.message)

    @mock.patch('ansible.module_utils.urls.open_url')
    def testRequestFailedWithReasonMessage(self, open_url_mock):
        reason = mock.MagicMock()
        reason.message = 'GitlabUserSendRequestTest.testRequestFailedWithReasonMessage'
        open_url_mock.side_effect = urllib2.URLError(reason)

        with self.assertRaises(library.gitlab_user.GitlabModuleInternalException) as ex:
            library.gitlab_user._send_request(
                'GET',
                'http://something.com',
                {'Content-Type': 'text/csv'},
                'something'
            )

        self.assertEqual('GitlabUserSendRequestTest.testRequestFailedWithReasonMessage', ex.exception.message)