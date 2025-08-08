from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Estado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str

    usuarios: list["Usuario"] = Relationship(back_populates="estado")
    negocios: list["Negocio"] = Relationship(back_populates="estado")
    


class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    slug: str

    negocios: list["Negocio"] = Relationship(back_populates="categoria")


class Perfil(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str

    usuarios: list["Usuario"] = Relationship(back_populates="perfil")


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    estado_id: int | None = Field(default=None, foreign_key="estado.id")
    estado: Optional[Estado] = Relationship(back_populates="usuarios")

    perfil_id: int | None = Field(default=None, foreign_key="perfil.id")
    perfil: Optional[Perfil] = Relationship(back_populates="usuarios")

    nombre: str
    correo: str
    telefono: str
    password: str
    token: str
    fecha: datetime = Field(default_factory=datetime.now)

    negocios: list["Negocio"] = Relationship(back_populates="usuario")


class Negocio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    estado_id: int | None = Field(default=None, foreign_key="estado.id")
    estado: Optional[Estado] = Relationship(back_populates="negocios")

    categoria_id: int | None = Field(default=None, foreign_key="categoria.id")
    categoria: Optional[Categoria] = Relationship(back_populates="negocios")

    usuario_id: int | None = Field(default=None, foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="negocios")

    nombre: str = Field(max_length=100)
    slug: str  = Field(max_length=100)
    correo: str  = Field(max_length=50)
    telefono: str  = Field(max_length=20)
    direccion: str= Field(max_length=100)
    logo: str 
    mapa:str
    descripcion: str
    fecha: datetime = Field(default_factory=datetime.now)

    platos: list["Platos"] = Relationship(back_populates="negocio")


class PlatosCategoria(SQLModel, table=True):
    id: int | None =Field(default=None, primary_key=True)
    nombre: str
    slug: str

    platos: list["Platos"] = Relationship(back_populates="platoscategoria")


class Platos(SQLModel, table=True):
    id: int | None =Field(default=None, primary_key=True)
    
    negocio_id: int | None = Field(default=None, foreign_key="negocio.id")
    negocio: Optional[Negocio] = Relationship(back_populates="platos")

    platoscategoria_id: int | None = Field(default=None, foreign_key="platoscategoria.id")
    platoscategoria: Optional[PlatosCategoria] = Relationship(back_populates="platos")

    nombre: str
    ingredientes: str
    precio: int
    foto: str