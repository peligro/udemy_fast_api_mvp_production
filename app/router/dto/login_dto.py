from pydantic import BaseModel


class LoginDto(BaseModel):
    correo: str
    password: str