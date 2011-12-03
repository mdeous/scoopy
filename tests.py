# -*- coding: utf-8 -*-


from unittest import TestCase
from scoopy import ScoopItAPI


class ScoopyTest(TestCase):
    mocked_data = {}

    def setUp(self):
        self.api = ScoopItAPI('FAKE_CONSUMER', 'FAKE_SECRET')
        self.api.oauth.request = self.mockedRequest

    def mockedRequest(self, url, params, method='GET'):
        return self.mocked_data[method]
