# -*- coding: utf-8 -*-
import time
import re

from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponseForbidden

import uamobile
import utils

class BPMobileMiddleware(object):
    def process_request(self, request):
        request.agent = uamobile.detect(request.META)
        if request.agent.is_nonmobile() or request.agent.is_docomo():
            return

        def _convert_dict(d, agent):
            for k, v in d.iteritems():
                if agent.is_softbank():
                    d[k] = utils.RE_UNI_EMOJI_SOFTBANK.sub(lambda m:utils.uni_softbank2docomo(m.group()), v)
                elif agent.is_ezweb():
                    d[k] = utils.RE_UNI_EMOJI_KDDI.sub(lambda m:utils.uni_kddi2docomo(m.group()), v)

        request.GET._mutable = True
        request.POST._mutable = True
        _convert_dict(request.GET, request.agent)
        _convert_dict(request.POST, request.agent)
        request.GET._mutable = False
        request.POST._mutable = False

class BPMobileConvertResponseMiddleware(object):
    def process_response(self, request, response):
        # encoding変換済みならスキップ
        if getattr(response, 'encoded', False):
            return response

        agent = uamobile.detect(request.META)

        if not agent.is_nonmobile():
            encoding = 'UTF-8'
            if response['content-type'].startswith('text'):
                c = unicode(response.content,'utf8')
                if agent.is_docomo():
                    response.content = c.encode('cp932','replace')
                    encoding = 'Shift_JIS'
                elif agent.is_ezweb():
                    c = utils.RE_UNI_EMOJI_KDDI.sub(lambda m:utils.kddi_uni2xuni(m.group()), c)
                    response.content = c.encode('cp932','replace')
                    encoding = 'Shift_JIS'
                elif agent.is_softbank():
                    c = utils.RE_UNI_EMOJI_DOCOMO.sub(lambda m:utils.uni_docomo2softbank(m.group()), c)
                    response.content = c.encode('utf8','replace')
            response['content-type'] = 'application/xhtml+xml; charset=%s' % encoding
        
        return response

class BPMobileSessionMiddleware(object):
    cache_key_name = 'session_key_%s'

    def get_agent(self, request):
        return getattr(request, 'agent', uamobile.detect(request.META))

    def get_cache_key(self, guid):
        return self.cache_key_name % guid

    def process_request(self, request):
        engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        agent = self.get_agent(request)
        if not agent.is_docomo():
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        else:
            if request.method == 'GET' and not request.GET.has_key('guid'):
                # guid=onを付与したURLにリダイレクト
                if request.is_secure():
                    # SSLだとiモードIDは使えない
                    protocol = 'https'
                else:
                    protocol = 'http'
                if request.GET:
                    query_string = '&guid=on'
                else:
                    query_string = '?guid=on'
                url = "%s://%s%s%s" % (protocol, request.get_host(), request.get_full_path(), query_string)
                return HttpResponseRedirect(url)
            if agent.guid:
                # cacheからセッションキーをとってくる
                session_key = cache.get(self.get_cache_key(agent.guid))
            else:
                session_key = None
        request.session = engine.SessionStore(session_key)

    def process_response(self, request, response):
        # If request.session was modified, or if response.session was set, save
        # those changes and set a session cookie.
        agent = self.get_agent(request)
        try:
            accessed = request.session.accessed
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                # Save the session data and refresh the client cookie.
                request.session.save()
                if not agent.is_docomo():
                    response.set_cookie(settings.SESSION_COOKIE_NAME,
                            request.session.session_key, max_age=max_age,
                            expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                            path=settings.SESSION_COOKIE_PATH,
                            secure=settings.SESSION_COOKIE_SECURE or None)
                else:
                    if agent.guid:
                        # memcacheにセッションキーをセット
                        session_key = cache.set(self.get_cache_key(agent.guid), request.session.session_key, settings.SESSION_COOKIE_AGE)
        return response

class BPMobileDenyBogusIPMiddleware(object):

    def get_agent(self, request):
        return getattr(request, 'agent', uamobile.detect(request.META))

    def process_request(self, request):
        agent = self.get_agent(request)
        if agent.is_nonmobile() or agent.is_bogus():
            return HttpResponseForbidden('403 Access Forbidden.')
