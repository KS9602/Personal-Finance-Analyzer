from pydantic import BaseModel

class LoginData(BaseModel):
    code: str
    code_verifier: str

