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
    import json # python>=2.6
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print "Python < 2.6 and simplejson not found, exiting."
        import sys
        sys.exit(2)


class ScoopItObject(object):
    """
    Ancestor of every ScoopIt data type, holds common stuff.
    """
    _convert_map = {}

    def __init__(self, raw_data):
        for key, value in raw_data.iteritems():
            if key in self._convert_map:
                setattr(self, key, self._convert_map[key](value))
            else:
                setattr(self, key, value)


class Topic(ScoopItObject):
    """
    Holds data related to a topic.
    """
    _convert_map = {
        'creator': lambda x: User(x),
        'pinnedPost': lambda x: Post(x),
        'curablePosts': lambda x: [Post(y) for y in x],
        'curatedPosts': lambda x: [Post(y) for y in x],
        'tags': lambda x: [TopicTag(y) for y in x],
    }

    def __init__(self, raw_data):
        self.curablePostCount = None
        self.unreadPostCount = None
        self.pinnedPost = None
        self.curablePosts = []
        self.curatedPosts = []
        super(Topic, self).__init__(raw_data)


class TopicTag(ScoopItObject):
    """
    Holds data related to a tag of a topic.
    """
    pass


class Post(ScoopItObject):
    """
    Holds data related to a post.
    """
    _convert_map = {
        'source': lambda x: Source(x),
        'comments': lambda x: [PostComment(y) for y in x],
        'topic': lambda x: Topic(x),
    }

    def __init__(self, raw_data):
        self.thanked = None
        self.topic = None
        super(Post, self).__init__(raw_data)


class PostComment(ScoopItObject):
    """
    Holds data related to a comment.
    """
    _convert_map = {'author': lambda x: User(x), }


class Source(ScoopItObject):
    """
    Holds data related to a source: something that suggests
    content to curate to users.
    """
    pass


class User(ScoopItObject):
    """
    Holds data related to a user.
    """
    _convert_map = {
        'sharers': lambda x: [Sharer(y) for y in x],
        'curatedTopics': lambda x: [Topic(y) for y in x],
    }

    def __init__(self, raw_data):
        self.sharers = []
        super(User, self).__init__(raw_data)


class Sharer(ScoopItObject):
    """
    Holds data related to a "sharer". A "sharer" is basically
    an account to a publish service the user registered in the
    dedicated website page (eg: twitter account, facebook
    account, tumblr account).
    """
    pass


class Notification(ScoopItObject):
    """
    Holds data related to a notification.
    """
    _convert_map = {'type': lambda x: NotificationType(x), }


class NotificationType(ScoopItObject):
    """
    Describes the type of a notification.
    """
    pass


class TopicStats(ScoopItObject):
    """
    Holds statistics related to a topic.
    """
    pass
