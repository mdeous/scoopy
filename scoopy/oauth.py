# -*- coding: utf-8 -*-
#
#    This file is part of scoopy.
#
#    Scoopy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Scoopy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Scoopy.  If not, see <http://www.gnu.org/licenses/>.
#

import cPickle
import os
import shelve
from time import time
from urllib import urlencode
from urlparse import parse_qsl

import oauth2

__all__ = [
    'REQUEST_TOKEN_URL',
    'ACCESS_TOKEN_URL',
    'AUTHORIZE_URL',
    'OAuthException',
    'OAuthRequestFailure',
    'OAuthTokenError',
    'OAuth',
]

BASE_URL = 'https://www.scoop.it'
REQUEST_TOKEN_URL = '%s/oauth/request' % BASE_URL
ACCESS_TOKEN_URL = '%s/oauth/access' % BASE_URL
AUTHORIZE_URL = '%s/oauth/authorize' % BASE_URL


#noinspection PyMissingConstructor
class OAuthException(Exception):
    """
    Basic exception for OAuth related errors.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class OAuthRequestFailure(OAuthException):
    """
    Exception raised when a request fails.
    """
    pass


class OAuthTokenError(OAuthException):
    """
    Exception raised when a token isn't set and
    an operation requiring one is performed.
    """
    pass


class OAuth(object):
    """
    Helper class for all OAuth related actions.

    Constructor parameters:
        - consumer_key (str): the application's API consumer key
        - consumer_secret (str): the application's API consumer secret
    """
    signature_method = oauth2.SignatureMethod_HMAC_SHA1()

    def __init__(self, consumer_key, consumer_secret):
        self.consumer = oauth2.Consumer(consumer_key, consumer_secret)
        self.client = oauth2.Client(self.consumer)
        self.token = None
        self.access_granted = False

    def save_token(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
        db = shelve.open(filepath, protocol=cPickle.HIGHEST_PROTOCOL)
        if self.token is None:
            raise OAuthTokenError('No token found, get one first')
        #TODO: if access is not granted, warn user the token saved will be a request_token
        db['oauth_token'] = self.token.key
        db['oauth_token_secret'] = self.token.secret
        db.close()

    def load_token(self, filepath):
        db = shelve.open(filepath, protocol=cPickle.HIGHEST_PROTOCOL)
        self.token = oauth2.Token(
            db['oauth_token'],
            db['oauth_token_secret']
        )
        self.client = oauth2.Client(self.consumer, self.token)
        db.close()

    def get_request_token(self):
        """
        Request the server for a request_token and return it.
        """
        response, content = self.client.request(REQUEST_TOKEN_URL, 'GET')
        if response['status'] != '200':
            raise OAuthRequestFailure(
                "Failed to get request_token (%s)" % response['status']
            )
        request_token = dict(parse_qsl(content))
        self.token = oauth2.Token(
            request_token['oauth_token'],
            request_token['oauth_token_secret']
        )

    def get_access_token_url(self, callback_url):
        """
        Generate the URL needed for the user to accept the application
        and return it.
        """
        if self.token is None:
            raise OAuthTokenError(
                "No request_token found, get one first"
            )
        #TODO: warn user if access already granted
        return "%s?oauth_token=%s&oauth_callback=%s" % (
            AUTHORIZE_URL,
            self.token.key,
            callback_url
        )

    def get_access_token(self, token_verifier):
        """
        Request the server for an access token and return it.
        """
        self.token.set_verifier(token_verifier)
        self.client = oauth2.Client(self.consumer, self.token)
        response, content = self.client.request(ACCESS_TOKEN_URL, 'POST')
        if response['status'] != '200':
            raise OAuthRequestFailure(
                "Failed to get access_token (%s)" % response['status']
            )
        self.access_granted = True
        access_token = dict(parse_qsl(content))
        self.token = oauth2.Token(
            access_token['oauth_token'],
            access_token['oauth_token_secret'],
        )
        self.client = oauth2.Client(self.consumer, self.token)

    def generate_request_params(self, params):
        """
        Given a dict of parameters, add the needed oauth_* parameters
        to it and an url-encoded string.
        """
        request_params = {
            'oauth_version':        '1.0',
            'oauth_nonce':          oauth2.generate_nonce(),
            'oauth_timestamp':      int(time()),
            'oauth_token':          self.token.key,
            'oauth_consumer_key':   self.consumer.key,
        }
        for key, value in params.iteritems():
            request_params[key] = value
        return urlencode(request_params)

    def request(self, url, params, method='GET'):
        return self.client.request(
            url,
            method=method,
            body=self.generate_request_params(params),
            headers={'Accept-encoding': 'gzip'},
        )
