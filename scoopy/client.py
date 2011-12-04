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
"""
.. module:: client

.. moduleauthor:: Mathieu D. (MatToufoutu) <mattoufootu[at]gmail.com>
"""

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
    'NOTIFICATIONS_URL',
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
NOTIFICATIONS_URL = '%s/api/1/notifications' % BASE_URL
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
    """
    #XXX: take care not to duplicate objets actions in ScoopItAPI and objects methods

    def __init__(self, consumer_key, consumer_secret):
        """
        :param consumer_key: The application's API consumer key.
        :type consumer_key: str.
        :param consumer_secret: The application's API consumer secret.
        """
        self.oauth = OAuth(consumer_key, consumer_secret)

    def get_oauth_request_token(self):
        """
        Ask the API server for an oauth request_token.

        :returns: None
        """
        self.oauth.get_request_token()

    def get_oauth_access_token_url(self, callback_url):
        """
        Generate an access authorization URL.

        :param callback_url: The url to which the user should be redirected.
        :type callback_url: str.
        :returns: str -- The url to authorize the application.
        """
        return self.oauth.get_access_token_url(callback_url)

    def get_oauth_access_token(self, token_verifier):
        """
        Ask the API server for an oauth access_token.

        :param token_verifier: The code returned by the access_token url.
        :type token_verifier: str.
        :returns: None.
        """
        self.oauth.get_access_token(token_verifier)

    def save_oauth_token(self, filepath):
        """
        Save the current OAuth token to a file.

        :param filepath: Path to the file where the token should be saved.
        :type filepath: str.
        :returns: None.
        """
        self.oauth.save_token(filepath)

    def load_oauth_token(self, filepath):
        """
        Load a previously saved OAuth token.

        :param filepath: Path to the file containing the token.
        :type filepath: str.
        :returns: None.
        """
        self.oauth.load_token(filepath)

    def request(self, url, params, method='GET'):
        """
        Make a request to an API end-point, request will be signed using
        the current OAuth token.

        :param url: The end-point url.
        :type url: str.
        :param params: Parameters to pass to the request.
        :type params: dict.
        :param method: The HTTP method used to perform the request.
        :type method: str.
        :returns: dict -- Data returned by the server.
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

        :param profile_id: Profile owner's ID (defaults to the current user).
        :type profile_id: int or None.
        :param curated: Numer of curated posts to retrieve for each
                        topic (defaults to 0).
        :type curated: int or None.
        :param curable: Number of curable posts to retrieve for each topic
                        where the user is curator (defaults to 0).
        :returns: An :class:`scoopy.datatypes.User` object.
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

    def topic(self, topic_id, curated=None, curable=None,
                  order=None, tag=None, since=None):
        """
        Access a topic data (list of posts, statistics).

        :param topic_id: The topic's ID.
        :type topic_id: int or None.
        :param curated: Number of curated posts to retrieve from the
                        topic (defaults to 30).
        :type curated: int or None.
        :param curable: Number of curable posts to retrieve from the
                        topic (defaults to 30).
        :type curable: int or None.
        :param order: Sort order of curated posts, can be 'tag', 'curationDate',
                      or 'user' (mandatory if 'since' parameter isn't specified).
        :type order: str.
        :param tag: Tag used to filter results (mandatory if 'order' is 'tag').
        :type tag: str.
        :param since: Only retrieve curated posts newer than this.
        :type since: :class:`scoopy.datatypes.Timestamp`.
        :return: tuple -- (:class:`scoopy.datatypes.Topic`, :class:`scoopy.datatypes.TopicStats`)
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

    def topic_reorder(self, topic_id, post_ids, start):
        #TODO: write ScoopItAPI.topic_reorder() method
        raise NotImplementedError

    def topic_follow(self, topic_id):
        self._topic_fum('follow', topic_id)
    def topic_unfollow(self, topic_id):
        self._topic_fum('unfollow', topic_id)
    def topic_markread(self, topic_id):
        self._topic_fum('markread', topic_id)
    def _topic_fum(self, action, topic_id):
        #TODO: write ScoopItAPI._topic_fum() method
        raise NotImplementedError

    def post(self, post_id):
        """
        Access a post data.

        :param post_id: The ID of the post.
        :type post_id: int.
        :return: a :class:`scoopy.datatypes.Post` object.
        """
        params = {
            'id': post_id,
        }
        response = self.request(POST_URL, params)
        return Post(self, response)

    def post_prepare(self, url):
        #TODO: write ScoopItAPI.post_prepare() method
        raise NotImplementedError

    def post_create(self, title, url, content, image_url, topic_id, share_on):
        #TODO: write ScoopItAPI.post_create() method
        raise NotImplementedError

    def post_comment(self, post_id, comment):
        #TODO: write ScoopItAPI.post_comment() method
        raise NotImplementedError

    def post_thank(self, post_id):
        #TODO: write ScoopItAPI.post_thank() method
        raise NotImplementedError

    def post_accept(self, post_id, title, content, image_url, share_on, topic_id):
        #TODO: write ScoopItAPI.post_accept() method
        raise NotImplementedError

    def post_forward(self, post_id, title, content, image_url, share_on, topic_id):
        #TODO: write ScoopItAPI.post_forward() method
        raise NotImplementedError

    def post_refuse(self, post_id, reason):
        #TODO: write ScoopItAPI.post_refuse() method
        raise NotImplementedError

    def post_delete(self, post_id):
        #TODO: write ScoopItAPI.post_delete() method
        raise NotImplementedError

    def post_edit(self, post_id, tags, title, content, image_url):
        #TODO: write ScoopItAPI.post_edit() method
        raise NotImplementedError

    def post_pin(self, post_id):
        #TODO: write ScoopItAPI.post_pin() method
        raise NotImplementedError

    def post_rescoop(self, post_id, topic_id):
        #TODO: write ScoopItAPI.post_rescoop() method
        raise NotImplementedError

    def post_share(self, post_id):
        #TODO: write ScoopItAPI.post_share() method
        raise NotImplementedError

    def notifications(self, since=None):
        """
        Notifications for the current user.

        :param since: Only get notifications newer than this.
        :type since: :class:`scoopy.datatypes.Timestamp` or None.
        :return: iterator -- :class:`scoopy.datatypes.Notification` objects.
        """
        params = {}
        if since is not None:
            params['since'] = since.value
        response = self.request(NOTIFICATIONS_URL, params)
        return [Notification(self, n) for n in response['notifications']]

    def compilation(self, since, count):
        """
        Get a compilation of followed topics of the current user.
        Posts are ordered by date.

        :param since: Only retrieve posts newer than this.
        :type since: :class:`scoopy.datatypes.Timestamp`.
        :param count: Maximum amount of posts to retrieve.
        :type count: int.
        :return: iterator -- :class:`scoopy.datatypes.Post` objects.
        """
        params = {
            'since': since.value,
            'count': count,
        }
        response = self.request(COMPILATION_URL, params)
        return [Post(self, p) for p in response['posts']]

    def test(self):
        #TODO: write ScoopItAPI.test() method
        raise NotImplementedError

    def search(self, type, query, page, lang):
        #TODO: write ScoopItAPI.search() method
        raise NotImplementedError

    def resolve(self, entity, short_name):
        """
        Resolve an object (topic or user) given its short name.

        :param entity: The type of entity to resolve ('user' or 'topic').
        :type entity: str.
        :param short_name: The short name to resolve.
        :type short_name: str.
        :return: str -- The ID corresponding to the given short name.
        """
        if entity.lower() not in ('user', 'topic'):
            raise ScoopItError("entity value can only be 'User' or 'Topic'")
        params = {
            'type': entity,
            'shortName': short_name,
        }
        response = self.request(RESOLVER_URL, params)
        return response['id']
