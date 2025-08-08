from pydantic import BaseModel, model_validator


class CategoriaDto(BaseModel):
    nombre: str

    
    @model_validator(mode='after')
    def validar_nombre(self):
        if not self.nombre or len(self.nombre.strip())<2:
            raise ValueError('nombre', 'El campo nombre debe tener al menos 2 caracteres')
        return self
    

