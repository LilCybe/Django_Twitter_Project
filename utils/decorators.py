from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(method='GET', params=None):
    """
    when using @required_params(params=['some_param'])
    this required_params functions should return a decorator function，
    the parameter of this decorator function
    is function view_func wrapped by @required_params
    """
    if params is None:
        params = []

    def decorator(view_func):
        """
        decorator function wraps parameters of view_func and send to _wrapped_view
        here the instance parameter is the self inside view_func
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            if method.lower() == 'get':
                data = request.query_params
            else:
                data = request.data
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            # check then use view_func wrapped by @required_params
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator