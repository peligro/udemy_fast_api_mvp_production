from pydantic import BaseModel

class GenericInterface(BaseModel):
    estado: str
    mensaje: str


class NegocioResponse(BaseModel):
    id: int
    nombre: str
    logo: str
    mapa: str
    facebook: str
    descripcion: str
    instagram: str
    twitter: str
    slug: str
    correo: str
    tiktok: str
    telefono: str
    estado_id: int
    estado: str
    usuario_id: int
    usuario: str
    categoria_id: int
    categoria: str
    direccion: str
    fecha: str  # formatted as DD/MM/YYYY

    class Config:
        from_attributes = True






class PlatoResponse(BaseModel):
    id: int
    nombre: str
    ingredientes: str
    precio: int
    foto: str
    platoscategoria: str 

    class Config:
        from_attributes = True


class NegocioSlugResponse(BaseModel):
    id: int
    nombre: str
    logo: str
    mapa: str
    facebook: str
    descripcion: str
    instagram: str
    twitter: str
    slug: str
    correo: str
    tiktok: str
    telefono: str
    estado_id: int
    estado: str
    usuario_id: int
    usuario: str
    categoria_id: int
    categoria: str
    direccion: str
    fecha: str
    platos: list[PlatoResponse] 

    class Config:
        from_attributes = True


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    telefono: str
    estado_id: int
    estado: str
    perfil_id: int
    perfil: str
    fecha: str 

    class Config:
        from_attributes = True



class LoginResponse(BaseModel):
    estado: str
    mensaje: str
    data: dict | None = None



