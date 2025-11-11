from django.shortcuts import render
from django.db import OperationalError
import logging

logger = logging.getLogger(__name__)

class SystemErrorMiddleware:
    """Catch DB/Server errors and show a friendly 500 page with a generic message.

    This middleware should be placed high in the MIDDLEWARE list (after SecurityMiddleware
    but before other app middleware) so it can intercept exceptions and render a
    friendly page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except OperationalError as exc:
            # DB connection issue
            logger.exception('Database operational error')
            return render(request, '500.html', status=500)
        except Exception as exc:
            # Generic server error
            logger.exception('Unhandled server error')
            return render(request, '500.html', status=500)
