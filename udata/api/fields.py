# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from dateutil.parser import parse

from flask import request, url_for
from flask_restplus.fields import *  # noqa


log = logging.getLogger(__name__)


class ISODateTime(String):
    __schema_format__ = 'date-time'

    def format(self, value):
        if isinstance(value, basestring):
            value = parse(value)
        return value.isoformat()


class Markdown(String):
    __schema_format__ = 'markdown'


class UrlFor(String):
    def __init__(self, endpoint, mapper=None, **kwargs):
        super(UrlFor, self).__init__(**kwargs)
        self.endpoint = endpoint
        self.mapper = mapper or self.default_mapper

    def default_mapper(self, obj):
        return {'id': str(obj.id)}

    def output(self, key, obj):
        return url_for(self.endpoint, _external=True, **self.mapper(obj))


class NextPageUrl(String):
    def output(self, key, obj):
        if not getattr(obj, 'has_next'):
            return None
        args = request.args.copy()
        args.update(request.view_args)
        args['page'] = obj.page + 1
        return url_for(request.endpoint, _external=True, **args)


class PreviousPageUrl(String):
    def output(self, key, obj):
        if not getattr(obj, 'has_prev'):
            return None
        args = request.args.copy()
        args.update(request.view_args)
        args['page'] = obj.page - 1
        return url_for(request.endpoint, _external=True, **args)


class ImageField(String):
    def __init__(self, size=None, **kwargs):
        super(ImageField, self).__init__(**kwargs)
        self.size = size

    def format(self, field):
        return (field(self.size, external=True)
                if self.size else field(external=True))


def pager(page_fields):
    pager_fields = {
        'data': List(Nested(page_fields), attribute='objects',
                     description='The page data'),
        'page': Integer(description='The current page', required=True, min=1),
        'page_size': Integer(description='The page size used for pagination',
                             required=True, min=0),
        'total': Integer(description='The total paginated items',
                         required=True, min=0),
        'next_page': NextPageUrl(description='The next page URL if exists'),
        'previous_page': PreviousPageUrl(
            description='The previous page URL if exists'),
        'facets': Raw(description='Search facets results if any'),
    }
    return pager_fields
