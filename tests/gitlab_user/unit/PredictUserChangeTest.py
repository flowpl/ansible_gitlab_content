# -*- coding: utf-8 -*-

import unittest
import ddt
import library.gitlab_user


@ddt.ddt
class PredictUserChangeTest(unittest.TestCase):

    def test_returnTrue_ifUserIsNone(self):
        result = library.gitlab_user._predict_user_change(None, None)
        self.assertTrue(result)

    def test_returnTrue_ifAdminChanged(self):
        result = library.gitlab_user._predict_user_change({"admin": True}, {"is_admin": False})
        self.assertTrue(result)

    @ddt.data(
        ("password", "password"),  # gitlab does not return password in GET /users. So password is always added, never changed
        ("name", "name"),
        ("skype", "skype"),
        ("linkedin", "linkedin"),
        ("twitter", "twitter"),
        ("website_url", "website_url"),
        ("projects_limit", 10),
        ("extern_uid", "extern_uid"),
        ("provider", "provider"),
        ("bio", "bio"),
        ("can_create_group", True),
    )
    @ddt.unpack
    def test_returnTrue_ifParamAdded(self, param_name, param_value):
        user = {"username": "username"}
        raw_data = {"username": "username", param_name: param_value}
        result = library.gitlab_user._predict_user_change(raw_data, user)
        self.assertTrue(result)

    @ddt.data(
        ("name", "name"),
        ("skype", "skype"),
        ("linkedin", "linkedin"),
        ("twitter", "twitter"),
        ("website_url", "website_url"),
        ("projects_limit", 10),
        ("extern_uid", "extern_uid"),
        ("provider", "provider"),
        ("bio", "bio"),
        ("can_create_group", True),
    )
    @ddt.unpack
    def test_returnTrue_ifParamChanged(self, param_name, param_value):
        user = {
            "username": "username",
            "name": "somename",
            "skype": "someskype",
            "linkedin": "somelinkedin",
            "twitter": "sometwitter",
            "website_url": "someurl",
            "projects_limit": 12,
            "extern_uid": "someuid",
            "provider": "someprovider",
            "bio": "somebio",
            "can_create_group": False
        }
        raw_data = {"username": "username", param_name: param_value}
        result = library.gitlab_user._predict_user_change(raw_data, user)
        self.assertTrue(result)

    def test_returnFalse_ifUserIsPresentAndNothingChanged(self):
        user = raw_data = {
            "username": "username",
            "name": "somename",
            "skype": "someskype",
            "linkedin": "somelinkedin",
            "twitter": "sometwitter",
            "website_url": "someurl",
            "projects_limit": 12,
            "extern_uid": "someuid",
            "provider": "someprovider",
            "bio": "somebio",
            "can_create_group": False
        }
        result = library.gitlab_user._predict_user_change(raw_data, user)
        self.assertFalse(result)