from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class Estado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str

    usuarios: list["Usuario"] = Relationship(back_populates="estado")
    negocios: list["Negocio"] = Relationship(back_populates="estado")


class Perfil(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str

    # Relación inversa con Usuario (opcional por ahora)
    usuarios: list["Usuario"] = Relationship(back_populates="perfil")

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    estado_id: int | None = Field(default=None, foreign_key="estado.id")
    estado: Optional[Estado] = Relationship(back_populates="usuarios")

    perfil_id: int | None = Field(default=None, foreign_key="perfil.id")  # 🔐 Clave foránea hacia Perfil
    perfil: Optional["Perfil"] = Relationship(back_populates="usuarios")  # ↔ Relación inversa
    
    nombre: str
    correo: str
    telefono: str
    password: str
    token: str
    fecha: datetime = Field(default_factory=datetime.now)

    negocios: list["Negocio"] = Relationship(back_populates="usuario")


class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    slug: str

    negocios: list["Negocio"] = Relationship(back_populates="categoria")


class Negocio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    estado_id: int | None = Field(default=None, foreign_key="estado.id")
    estado: Optional[Estado] = Relationship(back_populates="negocios")

    usuario_id: int | None = Field(default=None, foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="negocios")

    categoria_id: int | None = Field(default=None, foreign_key="categoria.id")
    categoria: Optional[Categoria] = Relationship(back_populates="negocios")

    # Campos normales
    nombre: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    correo: str = Field(max_length=100)
    telefono: str = Field(max_length=50)
    direccion: str = Field(max_length=100)
    logo: str
    facebook: str = Field(default="", max_length=100)
    instagram: str = Field(default="", max_length=100)
    twitter: str = Field(default="", max_length=100)
    tiktok: str = Field(default="", max_length=100)
    mapa: str
    descripcion: str
    fecha: datetime = Field(default_factory=datetime.now)

    # Relación inversa con Platos
    platos: list["Platos"] = Relationship(back_populates="negocio")


class PlatosCategoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    slug: str

    # Relación inversa con Platos
    platos: list["Platos"] = Relationship(back_populates="platoscategoria")


class Platos(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    ingredientes: str
    precio: int
    foto: str

    # Clave foránea hacia Negocio
    negocio_id: int | None = Field(default=None, foreign_key="negocio.id")
    negocio: Optional[Negocio] = Relationship(back_populates="platos")

    # Clave foránea hacia PlatosCategoria
    platoscategoria_id: int | None = Field(default=None, foreign_key="platoscategoria.id")
    platoscategoria: Optional[PlatosCategoria] = Relationship(back_populates="platos")


"""
from sqlmodel import SQLModel, Field

class Estado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
"""

