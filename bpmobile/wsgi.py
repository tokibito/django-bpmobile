from django.conf import settings
from django.core.handlers.wsgi import *
from django.core.exceptions import ImproperlyConfigured

def load_handler(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = __import__(module, {}, {}, [attr])
    except ImportError, e:
        raise ImproperlyConfigured, 'Error importing ditect encoding handler %s: "%s"' % (module, e)
    except ValueError, e:
        raise ImproperlyConfigured, 'Error importing ditect encoding handlers. Is DETECT_ENCODING_HANDLERS a correctly defined list or tuple?'
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured, 'Module "%s" does not define a "%s" ditect encoding handler' % (module, attr)
    return cls()

def get_handlers():
    from django.conf import settings
    handlers = []
    handler_pathes = getattr(settings, 'DETECT_ENCODING_HANDLERS', ('bpmobile.wsgi.UserAgentDetectEncoding',))
    for handler_path in handler_pathes:
        handlers.append(load_handler(handler_path))
    return handlers

def detect(envrion):
    for handler in get_handlers():
        try:
            encoding = handler.detect(envrion)
        except TypeError:
            continue
        if encoding is None:
            continue
        # encoding.handler = "%s.%s" % (handler.__module__, handler.__class__.__name__)
        return encoding

class UserAgentDetectEncoding(object):
    def detect(self, environ):
        encoding = None
        # try:
        import uamobile
        agent = uamobile.detect(environ)
        if agent.is_nonmobile() or agent.is_softbank():
            encoding = 'utf-8'
        else:
            encoding = 'cp932'
        return encoding
        # except:
        #     pass

class DetectEncodingWSGIRequest(WSGIRequest):
    """
    This request handler use the detect encoding handler class.
    """
    def __init__(self, environ):
        super(DetectEncodingWSGIRequest, self).__init__(environ)
        encoding = detect(environ)
        if encoding:
            self._set_encoding(encoding)

    def _get_raw_post_data(self):
        try:
            return self._raw_post_data
        except AttributeError:
            buf = StringIO()
            try:
                # CONTENT_LENGTH might be absent if POST doesn't have content at all (lighttpd)
                content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                # If CONTENT_LENGTH was empty string or not an integer, don't
                # error out. We've also seen None passed in here (against all
                # specs, but see ticket #8259), so we handle TypeError as well.
                content_length = 0
            if content_length > 0:
                safe_copyfileobj(self.environ['wsgi.input'], buf,
                        size=content_length)
            # convert the raw byte string data.
            self._raw_post_data = str(buf.getvalue())
            buf.close()
            return self._raw_post_data

    raw_post_data = property(_get_raw_post_data)
