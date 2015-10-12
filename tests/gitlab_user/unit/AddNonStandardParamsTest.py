# -*- coding: utf-8 -*-

import unittest
import library.gitlab_user


class AddNonStandardParamsTest(unittest.TestCase):

    def testAddAdmin(self):
        result = library.gitlab_user._add_non_standard_params({"admin": True}, {"something": "anything"})
        self.assertEqual({"something": "anything", "admin": True}, result)

    def testAddEmail(self):
        result = library.gitlab_user._add_non_standard_params(
            {"email": "someone@something.com"},
            {"something": "anything"}
        )
        self.assertEqual({"something": "anything", "email": "someone@something.com"}, result)

    def testAddEmailAndAdmin(self):
        result = library.gitlab_user._add_non_standard_params(
            {"email": "someone@something.com", "admin": False},
            {"something": "anything"}
        )
        self.assertEqual({"something": "anything", "admin": False, "email": "someone@something.com"}, result)
