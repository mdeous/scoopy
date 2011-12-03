# -*- coding: utf-8 -*-

import oauth2
import re
from tempfile import NamedTemporaryFile
from unittest import TestCase
from scoopy import ScoopItAPI
from scoopy import OAuth
try:
    import cPickle as pickle
except ImportError:
    import pickle

CONSUMER_KEY = 'FAKE_CONSUMER_KEY'
CONSUMER_SECRET = 'FAKE_CONSUMER_SECRET'
OAUTH_TOKEN = 'FAKE_OAUTH_TOKEN'
OAUTH_TOKEN_SECRET = 'FAKE_OAUTH_TOKEN_SECRET'


class ScoopyTest(TestCase):
    mocked_data = {}

    def setUp(self):
        self.api = ScoopItAPI(CONSUMER_KEY, CONSUMER_SECRET)
        self.api.oauth.request = self.mockedRequest

    def mockedRequest(self, url, params, method='GET'):
        return self.mocked_data[method]


class OAuthTest(TestCase):

    def setUp(self):
        self.oauth = OAuth(CONSUMER_KEY, CONSUMER_SECRET)
        self.oauth.token = oauth2.Token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        self.tmp = NamedTemporaryFile()

    def tearDown(self):
        self.tmp.close()

    def test_save_token(self):
        self.oauth.save_token(self.tmp.name)
        with open(self.tmp.name, 'rb') as infile:
            db = pickle.load(infile)
        self.assertEqual(
            db['oauth_token'], OAUTH_TOKEN,
            msg="Saved token ('%s') doesn't match expected value ('%s')" % (
                db['oauth_token'], OAUTH_TOKEN
            )
        )
        self.assertEqual(
            db['oauth_token_secret'], OAUTH_TOKEN_SECRET,
            msg="Saved token secret ('%s') doesn't match expected value ('%s')" % (
                db['oauth_token_secret'], OAUTH_TOKEN_SECRET
            )
        )

    def test_load_token(self):
        test_db = {
            'oauth_token': OAUTH_TOKEN,
            'oauth_token_secret': OAUTH_TOKEN_SECRET
        }
        with open(self.tmp.name, 'wb') as outfile:
            pickle.dump(test_db, outfile, pickle.HIGHEST_PROTOCOL)
        self.oauth.load_token(self.tmp.name)
        self.assertEqual(
            self.oauth.client.token.key, test_db['oauth_token'],
            msg="Loaded oauth token ('%s') doesn't match expected value ('%s')" % (
                self.oauth.client.token.key, test_db['oauth_token']
            )
        )
        self.assertEqual(
            self.oauth.client.token.secret, test_db['oauth_token_secret'],
            msg="Loaded oauth token secret ('%s') doesn't match expected value ('%s')" % (
                self.oauth.client.token.secret, test_db['oauth_token_secret']
            )
        )

    def test_generate_request_params(self):
        test_params = {
            'param1': 'firstParam',
            'param2': 'second /Pàram\\',
        }
        expected_re = re.compile(r'oauth_nonce=\d{8}&oauth_timestamp=\d{10}&oauth_consumer_key='+\
                                 CONSUMER_KEY+r'&oauth_version=1\.0&oauth_token='+\
                                 OAUTH_TOKEN+r'&param2=second\+%2FP%C3%A0ram%5C&param1=firstParam')
        result = self.oauth.generate_request_params(test_params)
        self.assertRegexpMatches(result, expected_re)
