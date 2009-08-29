from django.test import TestCase
from django.http import HttpRequest
from django.template import Template, RequestContext
import uamobile

from templatetags import mobile

class TemplateTagTest(TestCase):
    def setUp(self):
        self.agent_docomo = uamobile.docomo.DoCoMoUserAgent({}, {})
        self.agent_ezweb = uamobile.ezweb.EZwebUserAgent({}, {})
        self.agent_softbank = uamobile.softbank.SoftBankUserAgent({}, {})

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
