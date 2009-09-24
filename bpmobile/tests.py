from django.http import HttpRequest
from django.conf import settings
from django.template import Template, RequestContext

from test import TestCase
from middleware import BPMobileSessionMiddleware
from templatetags import mobile
from wsgi import DetectEncodingWSGIRequest

class TemplateTagTest(TestCase):
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

class SessionMiddlewareTest(TestCase):
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
