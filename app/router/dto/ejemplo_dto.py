from pydantic import BaseModel, model_validator, field_validator
from typing import Any
from pydantic import StrictInt


class EjemploDto(BaseModel):
    nombre: str
    descripcion: str
    precio: StrictInt
    verdadero: bool

    
    @model_validator(mode='after')
    def validar_nombre(self):
        if not self.nombre or len(self.nombre.strip())<2:
            raise ValueError('nombre', 'El campo nombre debe tener al menos 2 caracteres')
        return self
    

    @model_validator(mode='after')
    def validar_precio_valor(self):
        if self.precio <= 0:
            raise ValueError('precio', 'El precio debe ser mayor que cero')
        return self

    
    @field_validator('precio')
    def validar_tipo_precio(cls, valor: Any) -> int:
        if not isinstance(valor, int):
            raise ValueError('precio', 'El campo precio debe ser un número entero')
        return valor