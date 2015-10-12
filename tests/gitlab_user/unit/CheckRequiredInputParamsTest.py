# -*- coding: utf-8 -*-

import unittest
import library.gitlab_user
import ddt


@ddt.ddt
class CheckRequiredInputParamsTest(unittest.TestCase):

    def test_returnTrue_ifUserIsEmptyAndAllCreationParamsAreSet(self):
        raw_data = {"username": "username", "name": "name", "email": "email", "password": "password"}
        result = library.gitlab_user._check_required_input_params(raw_data, None)
        self.assertTrue(result)

    @ddt.data(
        {"username": "username", "name": "name", "email": "email"},
        {"username": "username", "name": "name", "password": "password"},
        {"username": "username", "email": "email", "password": "password"},
        {"name": "name", "email": "email", "password": "password"}
    )
    def test_returnFalse_ifUserIsEmptyAndRequiredCreationParamsAreMissing(self, raw_data):
        result = library.gitlab_user._check_required_input_params(raw_data, None)
        self.assertFalse(result)

    def test_returnTrue_ifUserIsNotEmptyAndAllUpdateParamsAreSet(self):
        raw_data = {"username": "username"}
        user = {"username": "username"}
        result = library.gitlab_user._check_required_input_params(raw_data, user)
        self.assertTrue(result)

    def testReturnFalse_ifUserIsNotEmptyAndRequiredUpdateParamsAreMissing(self):
        raw_data = {}
        user = {"username": "username"}
        result = library.gitlab_user._check_required_input_params(raw_data, user)
        self.assertFalse(result)
