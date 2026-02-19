from fastapi.exceptions import HTTPException

class AuthorizationException(HTTPException):        # TODO rozroznic potem na kategorie

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)



