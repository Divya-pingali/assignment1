from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, dict):
            message = response.data.get('detail') or response.data.get('error') or 'An error occurred.'
        else:
            message = 'An error occurred.'
        response.data = message
    return response
