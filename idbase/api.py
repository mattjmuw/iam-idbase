from django.http import HttpResponse
from idbase.exceptions import BadRequestError, InvalidSessionError, NotFoundError

import json
import logging


logger = logging.getLogger(__name__)

class RESTDispatch:
    """
    Handles passing on the request to the correct view
    method based on the request type.
    """

    def __init__(self, login_required=True):
        self.login_required = login_required

    def run(self, *args, **named_args):
        request = args[0]

        try:
            method = request.META['REQUEST_METHOD']

            if method not in ('GET', 'POST', 'PUT', 'DELETE') or not hasattr(self, method):
                raise BadRequestError('invalid method {}'.format(method))
            if self.login_required and not request.user.is_authenticated():
                raise InvalidSessionError('Unauthenticated user')
            response = getattr(self, method)(*args, **named_args)

        except BadRequestError as e:
            return self.http_error_response(e.message, status=400)
        except InvalidSessionError as e:
            return self.http_error_response(e.message if e.message else 'invalid session', status=401)
        except NotFoundError as e:
            return self.http_error_response(e.message, status=404)
        except Exception as e:
            logger.exception(e)
            return self.http_error_response(message=None, status=500)

        if isinstance(response, HttpResponse):
            return response
        else:
            return HttpResponse(json.dumps(response), status=200, content_type='application/json')


    def http_error_response(self, message=None, status=500):
        body = {'error_message': message if message else 'unspecified reason'}
        return HttpResponse(json.dumps(body), status=status, content_type='application/json')


class Login(RESTDispatch):
    def GET(self, request):
        return {
            'netid': request.user.username if request.user.is_authenticated() else None,
            'name': 'Place Holder'}