VERSION = (0, 2, 0, 'dev')
__version__ = '0.2dev'

from django.core.handlers.wsgi import WSGIHandler
from bpmobile.wsgi import DetectEncodingWSGIRequest

WSGIHandler.request_class = DetectEncodingWSGIRequest
