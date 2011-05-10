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

import datetime
import time

__all__ = [
    'Topic',
    'TopicTag',
    'Post',
    'PostComment',
    'Source',
    'User',
    'Sharer',
    'Notification',
    'NotificationType',
    'TopicStats',
]


class ScoopItObject(object):
    """
    Ancestor of every ScoopIt data type, holds common stuff.
    """
    _convert_map = {}

    def __init__(self, api, raw_data):
        self.api = api
        for key, value in raw_data.iteritems():
            if key in self._convert_map:
                setattr(self, key, self._convert_map[key](self.api, value))
            else:
                setattr(self, key, value)


class Topic(ScoopItObject):
    """
    Holds data related to a topic.
    """
    #TODO: handle post actions
    _convert_map = {
        'creator': lambda api, data: User(api, data),
        'pinnedPost': lambda api, data: Post(api, data),
        'curablePosts': lambda api, data: [Post(api, i) for i in data],
        'curatedPosts': lambda api, data: [Post(api, i) for i in data],
        'tags': lambda api, data: [TopicTag(api, i) for i in data],
    }

    def __init__(self, api, raw_data, stats=None):
        self.stats = TopicStats(api, stats)
        self.curablePostCount = None
        self.unreadPostCount = None
        self.pinnedPost = None
        self.curablePosts = []
        self.curatedPosts = []
        super(Topic, self).__init__(api, raw_data)

    def __str__(self):
        return "<Topic(name=%d)>" % self.name


class TopicTag(ScoopItObject):
    """
    Holds data related to a tag of a topic.
    """
    def __str__(self):
        return "<TopicTag(tag='%s')>" % self.tag


class Post(ScoopItObject):
    """
    Holds data related to a post.
    """
    #TODO: handle post actions
    _convert_map = {
        'source': lambda api, data: Source(api, data),
        'publicationDate': lambda api, data: Timestamp(data),
        'curationDate': lambda api, data: Timestamp(data),
        'comments': lambda api, data: [PostComment(api, i) for i in data],
        'topic': lambda api, data: Topic(api, data),
    }

    def __init__(self, api, raw_data):
        self.thanked = None
        self.topic = None
        super(Post, self).__init__(api, raw_data)

    def __str__(self):
        return "<Post(title='%s')>" % self.title


class PostComment(ScoopItObject):
    """
    Holds data related to a comment.
    """
    _convert_map = {
        'date': lambda api, data: Timestamp(data),
        'author': lambda api, data: User(api, data),
    }

    def __str__(self):
        return "<PostComment(author='%s')>" % self.author


class Source(ScoopItObject):
    """
    Holds data related to a source: something that suggests
    content to curate to users.
    """
    def __str__(self):
        return "<Source(name='%s')>" % self.name


class User(ScoopItObject):
    """
    Holds data related to a user.
    """
    _convert_map = {
        'sharers': lambda api, data: [Sharer(api, i) for i in data],
        'curatedTopics': lambda api, data: [Topic(api, i) for i in data],
    }

    def __init__(self, api, raw_data):
        self.sharers = []
        super(User, self).__init__(api, raw_data)

    def __str__(self):
        return "<User(name='%s')>" % self.name


class Sharer(ScoopItObject):
    """
    Holds data related to a "sharer". A "sharer" is basically
    an account to a publish service the user registered in the
    dedicated website page (eg: twitter account, facebook
    account, tumblr account).
    """
    def __str__(self):
        return "<Sharer(name='%s')>" % self.name


class Notification(ScoopItObject):
    """
    Holds data related to a notification.
    """
    _convert_map = {'type': lambda api, data: NotificationType(api, data), }
    #TODO: find how to represent the notification_type
    #TODO: (simply an enum, really needs its own object?)

    def __str__(self):
        return "<Notification(type='%s')>" % self.type


class NotificationType(ScoopItObject):
    """
    Describes the type of a notification.
    """
    #TODO: find how to represent it in __str__
    pass


class TopicStats(ScoopItObject):
    """
    Holds statistics related to a topic.
    """
    def __str__(self):
        return "<TopicStats(creatorName='%s')>" % self.creatorName


class Timestamp(object):
    """
    A timestamp object (what else to say?).
    This class also provides shortcuts to create Timestamp
    objects for 'yesterday', 'last_month', and 'last_year'.

    Constructor parameters:
      - value (int): the timestamp value
    """
    one_day = datetime.timedelta(1)
    one_month = datetime.timedelta(30)
    one_year = datetime.timedelta(365)

    def __init__(self, value):
        self.value = value

    def __str__(self):
        datetime_str = datetime.datetime.fromtimestamp(self.value)
        return "<Timestamp(value='%s')>" % str(datetime_str)

    @classmethod
    def from_datetime(cls, dt):
        return Timestamp((int(time.mktime(dt.timetuple()))))

    @classmethod
    def yesterday(cls):
        day = datetime.date.today() - Timestamp.one_day
        return Timestamp(Timestamp.from_datetime(day).value)

    @classmethod
    def last_month(cls):
        day = datetime.date.today() - Timestamp.one_month
        return Timestamp(Timestamp.from_datetime(day).value)

    @classmethod
    def last_year(cls):
        day = datetime.date.today() - Timestamp.one_year
        return Timestamp(Timestamp.from_datetime(day).value)
