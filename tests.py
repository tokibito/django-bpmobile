# coding: utf-8
"""
Standalone django model test with a 'memory-only-django-installation'.
You can play with a django model without a complete django app installation.
http://www.djangosnippets.org/snippets/1044/
"""

import os

APP_LABEL = os.path.splitext(os.path.basename(__file__))[0]

os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
from django.conf import global_settings

global_settings.INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'bpmobile',
)
global_settings.DATABASE_ENGINE = "sqlite3"
global_settings.DATABASE_NAME = ":memory:"
global_settings.DATABASE_SUPPORTS_TRANSACTIONS = False

from django.core.management import sql

from django.core.management.color import no_style
STYLE = no_style()

def create_table(*models):
    """ Create all tables for the given models """
    from django.db import connection
    cursor = connection.cursor()
    def execute(statements):
        for statement in statements:
            try:
                cursor.execute(statement)
            except:
                pass

    for model in models:
        execute(connection.creation.sql_create_model(model, STYLE)[0])
        execute(connection.creation.sql_indexes_for_model(model, STYLE))
        #execute(sql.custom_sql_for_model(model, STYLE))
        execute(connection.creation.sql_for_many_to_many(model, STYLE))

#______________________________________________________________________________
import sys
import unittest

from django.http import HttpRequest
from django.conf import settings
from django.template import Template, RequestContext

#from bpmobile.test import TestCase
from bpmobile.middleware import BPMobileSessionMiddleware
from bpmobile.templatetags import mobile
from bpmobile.wsgi import DetectEncodingWSGIRequest
from bpmobile.utils import useragent

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        sys.modules['tests.models'] = None
        from django.core import management
        management.call_command('syncdb', verbosity=1, interactive=False)

        self.agent_docomo = useragent.docomo.DoCoMoUserAgent({}, {})
        self.agent_ezweb = useragent.ezweb.EZwebUserAgent({}, {})
        self.agent_softbank = useragent.softbank.SoftBankUserAgent({}, {})

class TemplateTagTest(BaseTestCase):
    def test_emoji_tag_docomo(self):
        req = HttpRequest()
        req.agent = self.agent_docomo
        t = Template('{% load mobile %}{% emoji "BLACK SUN WITH RAYS" %}')
        c = RequestContext(req)
        try:
            content = t.render(c)
        except:
            self.fail()
        self.failUnlessEqual(content, u'\ue63e')

class SessionMiddlewareTest(BaseTestCase):
    def test_guid_redirect(self):
        if not 'django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE_CLASSES:
            self.fail('Django session middleware is not installed.')

        req = DetectEncodingWSGIRequest({
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': 80,
            'QUERY_STRING': 'abc=def&foo=bar',
            'REQUEST_METHOD': 'GET',
        })
        req.agent = self.agent_docomo

        middleware = BPMobileSessionMiddleware()

        res = middleware.process_request(req)
        self.failUnless(res, 'not redirected')
        self.failUnlessEqual(res.status_code, 302)
        self.failUnlessEqual(res['Location'], 'http://example.com/?abc=def&foo=bar&guid=on')
