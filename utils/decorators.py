from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(request_att='query_params', params=None):
    """
    when using @required_params(params=['some_param])
    this required_params should return a decorator function, this decorator param
    is view_func that is wrapped by @required_param
    :param request_att:
    :param params:
    :return:
    """
    if params is None:
        params = []

    def decorator(view_func):
        """
        decorator parse view_func through wraps and pass to _wrappped_view
        instance actually is  self in view_func
        :param view_func:
        :return:
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            data = getattr(request, request_att)
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request.'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            # after check, then call view_func
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator