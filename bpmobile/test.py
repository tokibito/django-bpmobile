# coding:utf-8
from django.test import TestCase as DjangoTestCase

import uamobile

class TestCase(DjangoTestCase):
    def _pre_setup(self):
        super(TestCase, self)._pre_setup()

        self.agent_docomo = uamobile.docomo.DoCoMoUserAgent({}, {})
        self.agent_ezweb = uamobile.ezweb.EZwebUserAgent({}, {})
        self.agent_softbank = uamobile.softbank.SoftBankUserAgent({}, {})
