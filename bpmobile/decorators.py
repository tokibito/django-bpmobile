from django.conf import settings

def encoded_response(view_func=None, encoding=None, charset=None, content_type=None):
    """
    mark encoded
    """
    def decorate(view_func):
        def decorate_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            _content_type = content_type or 'application/xhtml+xml'
            _encoding = encoding or 'utf-8'
            _charset = charset or _encoding
            response.content = unicode(response.content, settings.DEFAULT_CHARSET).encode(_encoding)
            response['content-type'] = '%s; charset=%s' % (_content_type, _charset)
            response.encoded = True
            return response
        return decorate_view
    if view_func:
        return decorate(view_func)
    return decorate
