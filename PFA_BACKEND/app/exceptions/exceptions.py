from fastapi.exceptions import HTTPException

class AuthorizationException(HTTPException):        # TODO rozroznic potem na kategorie

    def __init__(self, status_code: int = 401, detail: str = "Unauthorized"):
        super().__init__(status_code=status_code, detail=detail)

