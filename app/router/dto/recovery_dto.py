from pydantic import BaseModel


class RecoveryDto(BaseModel):
    correo: str


class RecoveryUpdateDto(BaseModel):
    password: str