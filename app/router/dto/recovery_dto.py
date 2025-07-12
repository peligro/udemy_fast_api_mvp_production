from pydantic import BaseModel, model_validator, field_validator
from pydantic import StrictInt
from typing import Any

class RecoveryDto(BaseModel):
    correo: str


    

