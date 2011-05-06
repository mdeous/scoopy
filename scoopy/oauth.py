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

from time import time
from urlparse import parse_qsl

import oauth2


BASE_URL = 'https://www.scoop.it'
REQUEST_TOKEN_URL = '%s/oauth/request' % BASE_URL
ACCESS_TOKEN_URL = '%s/oauth/access' % BASE_URL
AUTHORIZE_URL = '%s/oauth/authorize' % BASE_URL


class OAuthException(Exception):
    """
    Basic exception for OAuth related errors.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class OAuth(object):
    """
    Helper class for all OAuth related actions.

    Constructor params:
        - consumer_key (str): the application's API consumer key
        - consumer_secret (str): the application's API consumer secret
    """
    def __init__(self, consumer_key, consumer_secret):
        self.consumer = oauth2.Consumer(consumer_key, consumer_secret)
        self.client = oauth2.Client(self.consumer)
        self.request_token = None
        self.request_token_secret = None
        self.access_token = None
        self.access_token_secret = None

    def get_request_token(self):
        """
        Request the server for a request_token and return it.
        """
        response, content = self.client.request(REQUEST_TOKEN_URL, 'GET')
        if response['status'] != '200':
            raise OAuthException("Failed to get request token (%s)" % response['status'])
        request_token = dict(parse_qsl(content))
        self.request_token = request_token['oauth_token']
        self.request_token_secret = request_token['oauth_token_secret']
        return self.request_token, self.request_token_secret

    def get_access_token_url(self):
        """
        Generate the URL needed for the user to accept the application and return it.
        """
        if self.request_token is None:
            raise OAuthException("Request token is not set")
        return "%s?oauth_token=%s" % (AUTHORIZE_URL, self.request_token)

    def get_access_token(self, token_verifier):
        """
        Request the server for an access token and return it.
        """
        token = oauth2.Token(self.request_token, self.request_token_secret)
        token.set_verifier(token_verifier)
        self.client = oauth2.Client(self.consumer, token)
        response, content = self.client.request(ACCESS_TOKEN_URL, 'POST')
        access_token = dict(parse_qsl(content))
        self.access_token = access_token['oauth_token']
        self.access_token_secret = access_token['oauth_token_secret']
        return self.access_token, self.access_token_secret
