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

try:
    import json # python >= 2.6
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print("Python < 2.6 and simplejson not found, exiting.")
        import sys
        sys.exit(2)

from scoopy.datatypes import Notification, Post, User, Topic
from scoopy.oauth import OAuth

__all__ = [
    'PROFILE_URL',
    'TOPIC_URL',
    'POST_URL',
    'TEST_URL',
    'NOTIFICATION_URL',
    'COMPILATION_URL',
    'RESOLVER_URL',
    'ScoopItAPI',
    'ScoopItError',
]

BASE_URL = 'http://www.scoop.it'
PROFILE_URL = '%s/api/1/profile' % BASE_URL
TOPIC_URL = '%s/api/1/topic' % BASE_URL
POST_URL = '%s/api/1/post' % BASE_URL
TEST_URL = '%s/api/1/test' % BASE_URL
NOTIFICATION_URL = '%s/api/1/notification' % BASE_URL
COMPILATION_URL = '%s/api/1/compilation' % BASE_URL
RESOLVER_URL = '%s/api/1/resolver' % BASE_URL

ERROR_MESSAGES = {
    '400': 'Bad Request',
    '401': 'Unauthorized',
    '403': 'Forbidden',
    '404': 'Not Found',
    '405': 'Method Not Allowed',
}


class ScoopItError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class ScoopItAPI(object):
    """
    Main class to access the Scoop.it API.

    Constructor parameters:
      - consumer_key: the application's API consumer key
      - consumer_secret: the application's API consumer secret
    """

    def __init__(self, consumer_key, consumer_secret):
        self.oauth = OAuth(consumer_key, consumer_secret)

    def get_oauth_request_token(self):
        """
        Ask the API server for an oauth request_token.
        """
        self.oauth.get_request_token()

    def get_oauth_access_token_url(self, callback_url):
        """
        Generate an access authorization URL.

        Parameters:
          - callback_url (str): the url where the user should be redirected

        Returns: the URL the user should follow to allow the application
        """
        return self.oauth.get_access_token_url(callback_url)

    def get_oauth_access_token(self, token_verifier):
        """
        Ask the API server for an oauth access_token.

        Parameters:
          - token_verifier (str): the code returned by the access_token url
        """
        self.oauth.get_access_token(token_verifier)

    def save_oauth_token(self, filepath):
        """
        Save the current OAuth token to a file.

        Parameters:
          - filepath (str): path to the file where the token will be saved
        """
        self.oauth.save_token(filepath)

    def load_oauth_token(self, filepath):
        """
        Load a previously saved OAuth token.

        Parameters:
          - filepath (str): path to the file containing the token
        """
        self.oauth.load_token(filepath)

    def request(self, url, params, method='GET'):
        """
        Make a request to an API end-point, request will be signed using
        the current OAuth token.

        Parameters:
          - url (str): the end-point URL
          - params (dict): parameters to pass into the request
          - method (str): the method used to perform the request

        Returns: a dict containing requested data
        """
        status, data = self.oauth.request(url, params, method)
        data = json.loads(data)
        if not data['success']:
            raise ScoopItError(
                "%s %s: %s" % (
                    status['status'],
                    ERROR_MESSAGES[status['status']],
                    data['error']
                ))
        return data

    def get_profile(self, profile_id=None, curated=None, curable=None):
        """
        Access a user's profile.

        Parameters:
          - profile_id (int): id of the profile's owned (optional, defaults to
                              the current user)
          - curated (int): number of curated posts to retrieve for each topic
                           present in user data (optional, defaults to 0)
          - curable (int): number of curable posts to retrieve for each topic
                           the current user is the curator (optional, defaults
                           to 0)

        Returns: a 'User' object
        """
        if (profile_id is not None) and (curable is not None):
            raise ScoopItError('profile_id and curable options are exclusive')
        params = {}
        if profile_id is not None:
            params['id'] = profile_id
        if curated is not None:
            params['curated'] = curated
        if curable is not None:
            params['curable'] = curable
        response = self.request(PROFILE_URL, params)
        return User(self, response['user'])

    def get_topic(self, topic_id, curated=None, curable=None,
                  order=None, tag=None, since=None):
        """
        Access a topic data (list of posts, statistics).

        Parameters:
          - topic_id (int): the id of the topic
          - curated (int): number of curated posts to retrieve from
                           this topic (optional, defaults to 30)
          - curable (int): number of curable posts to retrieve for
                           this topic, this parameter is ignored if the
                           current user is the curator of this topic
          - order (str): sort order of the curated posts, can be 'tag',
                         'curationDate', or 'user' (mandatory if 'since'
                         parameter is not specified
          - tag (str): tag used to filter results (mandatory if 'order'=='tag')
          - since (Timestamp): only retrieve curated posts newer than this

        Returns: a '(Topic, TopicStats)' tuple
        """
        # check for mandatory options
        if (curated is not None) and (curable is not None):
            raise ScoopItError('curated and curable options are exclusive')
        if (since is None) and (order is None):
            raise ScoopItError('at least order or since must be specified')
        if (order is not None) and (order not in ('tag', 'curationDate', 'user')):
            raise ScoopItError("order can only be 'tag', 'curationDate', or 'user'")
        if (order == 'tag') and (tag is None):
            raise ScoopItError("tag must be specified if order is 'tag'")
        # populate params
        params = {
            'id': topic_id,
        }
        if curated is not None:
            params['curated'] = curated
        if curable is not None:
            params['curable'] = curable
        if order is not None:
            params['order'] = order
        if tag is not None:
            params['tag'] = tag
        if since is not None:
            params['since'] = since.value
        response = self.request(TOPIC_URL, params)
        return Topic(self, response['topic'], response['stats'])

    def get_post(self, post_id):
        """
        Access a post data.

        Parameters:
          - post_id (int): id of the post

        Returns: a 'Post' object
        """
        params = {
            'id': post_id,
        }
        response = self.request(POST_URL, params)
        return Post(self, response)

    def get_notifications(self, since=None):
        """
        Notifications for the current user.

        Parameters:
          - since (Timestamp): only get notifications newer than this

        Returns: an iterator containing 'Notification' objects
        """
        params = {}
        if since is not None:
            params['since'] = since.value
        response = self.request(NOTIFICATION_URL, params)
        return [Notification(self, n) for n in response['notifications']]

    def get_compilation(self, since, count):
        """
        Get a compilation of followed topics of the current user.
        Posts are ordered by date.

        Parameters:
          - since (Timestamp): no posts older than this will be returned
          - count (int): maximum number of posts to return

        Returns: an iterator containing 'Post' objects
        """
        params = {
            'since': since.value,
            'count': count,
        }
        response = self.request(COMPILATION_URL, params)
        return [Post(self, p) for p in response['posts']]

    def resolve(self, type, short_name):
        """
        Resolve an object (topic or user) given its short name.

        Parameters:
          - type (str): 'User' or 'Topic'
          - short_name (str): a short name

        Returns: the id corresponding to the given short name
        """
        if type.lower() not in ('user', 'topic'):
            raise ScoopItError("type value can only be 'User' or 'Topic'")
        params = {
            'type': type,
            'shortName': short_name,
        }
        response = self.request(RESOLVER_URL, params)
        return response['id']
