class CustomError(Exception):
    def __init__(self, message: str, status_code: int = 500, **kwargs):
        self.message = message
        self.status_code = status_code
        self.extra_data = kwargs
        super().__init__(self.message)


class UnauthorizedAccessError(CustomError):
    def __init__(self, message='Unauthorized access'):
        super().__init__(message, status_code=403)


class NotFoundError(CustomError):
    def __init__(self, entity: str, message=None):
        if not message:
            message = f'Unable to retrieve {entity}'
        super().__init__(message, status_code=404)


def handle_error(error: Exception):
    if isinstance(error, CustomError):
        response = {'statusCode': error.status_code, 'body': {'msg': error.message}}
        if error.extra_data:
            response['body'].update(error.extra_data)
        return response

    return {'statusCode': 500, 'body': {'msg': 'An unexpected error occurred'}}
