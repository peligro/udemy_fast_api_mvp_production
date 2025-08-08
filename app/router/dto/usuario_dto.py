from pydantic import BaseModel, model_validator
from typing import Optional


class UsuarioDto(BaseModel):
    estado_id: Optional[int] = None
    editar: Optional[int] = None
    perfil_id: int
    nombre: str
    correo: str
    telefono: str 
    password: str


    

    

"""
{
    "estado_id":1,
    "perfil_id":2,
    "nombre":"Juan Pérez",
    "correo":"juanito@gmail.com",
    "telefono":"123456",
    "password":"su casa en el árbol"
}
"""