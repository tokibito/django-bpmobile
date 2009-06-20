__version__ = '0.1'

from django.core.handlers.wsgi import WSGIHandler
from bpmobile.wsgi import DetectEncodingWSGIRequest

WSGIHandler.request_class = DetectEncodingWSGIRequest
